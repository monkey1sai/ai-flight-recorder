from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Iterator
from urllib.parse import urlparse
from uuid import UUID, uuid4

import pg8000.dbapi

from apps.api.app.cognitive import build_task_state_view, ensure_cognitive_state
from apps.api.app.why import ensure_why_records
from packages.schema.flight_recorder_schema import (
    ArtifactRecord,
    AuditEventRecord,
    ClaimEvidenceFlowView,
    ClaimRecord,
    EvaluationRecord,
    EvidenceEdgeRecord,
    ExplanationRecord,
    IngestReceipt,
    InterventionRecord,
    ObservationRecord,
    PlanVersionRecord,
    PolicyRuleRecord,
    ReplayFrameView,
    ResearchCorpusView,
    ResearchDocumentRecord,
    ResearchSearchResponse,
    ResearchSyncCursorRecord,
    ResearchSyncReceipt,
    ResearchSyncRunRecord,
    RetentionPolicyRecord,
    SessionRecord,
    StateDeltaRecord,
    StateDiffEntryView,
    StateSnapshotRecord,
    StepRecord,
    TaskRecord,
    TaskStateView,
    TimelineEntryView,
    TraceBundleView,
    TraceRecord,
    TraceSummaryView,
)

from .helpers import (
    build_claim_flows,
    build_replay,
    build_state_diffs,
    build_timeline,
    build_trace_summaries,
)


@dataclass(slots=True)
class PostgresConnectionConfig:
    database: str
    user: str
    password: str
    host: str
    port: int

    @classmethod
    def from_dsn(cls, dsn: str) -> "PostgresConnectionConfig":
        parsed = urlparse(dsn)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
        return cls(
            database=parsed.path.lstrip("/"),
            user=parsed.username or "postgres",
            password=parsed.password or "",
            host=parsed.hostname or "localhost",
            port=parsed.port or 5432,
        )


class PostgresTraceRepository:
    def __init__(self, database_url: str) -> None:
        self._config = PostgresConnectionConfig.from_dsn(database_url)

    @contextmanager
    def _connect(self) -> Iterator[pg8000.dbapi.Connection]:
        connection = pg8000.dbapi.connect(
            user=self._config.user,
            password=self._config.password,
            host=self._config.host,
            port=self._config.port,
            database=self._config.database,
        )
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def ping(self) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute("select 1")
            cursor.fetchall()

    def execute_script(self, sql: str) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(sql)

    def ensure_migration_table(self) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                create table if not exists schema_migrations (
                    name text primary key,
                    applied_at timestamptz not null default now()
                )
                """
            )

    def has_migration(self, name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "select 1 from schema_migrations where name = %s",
                [name],
            )
            return cursor.fetchone() is not None

    def record_migration(self, name: str) -> None:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                insert into schema_migrations (name)
                values (%s)
                on conflict (name) do nothing
                """,
                [name],
            )

    def table_exists(self, name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                select 1
                from information_schema.tables
                where table_schema = 'public' and table_name = %s
                """,
                [name],
            )
            return cursor.fetchone() is not None

    def type_exists(self, name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                select 1
                from pg_type t
                join pg_namespace n on n.oid = t.typnamespace
                where n.nspname = 'public' and t.typname = %s
                """,
                [name],
            )
            return cursor.fetchone() is not None

    def list_traces(self) -> list[TraceSummaryView]:
        trace_ids = self._list_trace_ids()
        bundles = [self.get_trace_bundle(trace_id) for trace_id in trace_ids]
        audit_lookup = {trace_id: self.list_audit_events(trace_id) for trace_id in trace_ids}
        return build_trace_summaries(
            [bundle for bundle in bundles if bundle is not None],
            audit_lookup,
        )

    def get_trace_bundle(self, trace_id: UUID) -> TraceBundleView | None:
        trace_row = self._fetch_one(
            """
            select * from traces
            where id = %s::uuid
            """,
            [str(trace_id)],
        )
        if trace_row is None:
            return None

        session_row = self._fetch_one(
            """
            select * from sessions
            where id = %s::uuid
            """,
            [str(trace_row["session_id"])],
        )
        if session_row is None:
            return None

        tasks = self._fetch_models(
            TaskRecord,
            "select * from tasks where trace_id = %s::uuid order by created_at",
            [str(trace_id)],
            empty_on=[],
        )
        task_ids = [str(task.id) for task in tasks]
        steps = [
            self._model(StepRecord, row)
            for row in self._fetch_all(
                "select * from steps where trace_id = %s::uuid order by step_index",
                [str(trace_id)],
            )
        ]
        step_ids = [str(step.id) for step in steps]

        observations = self._fetch_models(
            ObservationRecord,
            "select * from observations where step_id = any(%s::uuid[]) order by created_at",
            [step_ids],
            empty_on=[],
        )
        state_deltas = self._fetch_models(
            StateDeltaRecord,
            "select * from state_deltas where step_id = any(%s::uuid[]) order by created_at",
            [step_ids],
            empty_on=[],
        )
        plan_versions = self._fetch_models(
            PlanVersionRecord,
            "select * from plan_versions where task_id = any(%s::uuid[]) order by revision",
            [task_ids],
            empty_on=[],
        )
        state_snapshots = self._fetch_models(
            StateSnapshotRecord,
            "select * from state_snapshots where trace_id = %s::uuid order by snapshot_index",
            [str(trace_id)],
            empty_on=[],
        )
        artifact_ids = {
            str(item.source_artifact_id)
            for item in observations
            if item.source_artifact_id is not None
        }
        claims = self._fetch_models(
            ClaimRecord,
            "select * from claims where trace_id = %s::uuid order by position_index",
            [str(trace_id)],
        )
        claim_ids = [str(item.id) for item in claims]
        evidence_edges = self._fetch_models(
            EvidenceEdgeRecord,
            """
            select * from evidence_edges
            where (from_kind = 'claim' and from_id = any(%s::uuid[]))
               or (to_kind = 'step' and to_id = any(%s::uuid[]))
               or (to_kind = 'artifact' and to_id = any(%s::uuid[]))
            order by created_at
            """,
            [
                claim_ids or [str(uuid4())],
                step_ids or [str(uuid4())],
                list(artifact_ids) or [str(uuid4())],
            ],
            empty_on=[],
        )
        artifact_ids.update(
            str(edge.to_id) for edge in evidence_edges if str(edge.to_kind) == "artifact"
        )
        artifacts = self._fetch_models(
            ArtifactRecord,
            "select * from artifacts where id = any(%s::uuid[]) order by created_at",
            [list(artifact_ids)],
            empty_on=[],
        )
        explanations = self._fetch_models(
            ExplanationRecord,
            (
                "select * from explanation_records "
                "where claim_id = any(%s::uuid[]) order by created_at"
            ),
            [claim_ids],
            empty_on=[],
        )
        evaluations = self._fetch_models(
            EvaluationRecord,
            "select * from evaluations where trace_id = %s::uuid order by created_at",
            [str(trace_id)],
            empty_on=[],
        )
        interventions = self._fetch_models(
            InterventionRecord,
            "select * from interventions where trace_id = %s::uuid order by created_at",
            [str(trace_id)],
            empty_on=[],
        )

        return TraceBundleView(
            session=self._model(SessionRecord, session_row),
            trace=self._model(TraceRecord, trace_row),
            tasks=tasks,
            plan_versions=plan_versions,
            state_snapshots=state_snapshots,
            steps=steps,
            observations=observations,
            state_deltas=state_deltas,
            artifacts=artifacts,
            evidence_edges=evidence_edges,
            claims=claims,
            explanations=explanations,
            evaluations=evaluations,
            interventions=interventions,
            audit_events=self.list_audit_events(trace_id),
            policies=self.list_policies(),
            retention=self.list_retention(),
        )

    def upsert_bundle(self, bundle: TraceBundleView) -> IngestReceipt:
        bundle = ensure_cognitive_state(bundle)
        bundle = ensure_why_records(bundle)
        with self._connect() as connection:
            cursor = connection.cursor()
            self._upsert_session(cursor, bundle.session)
            provisional_trace = (
                bundle.trace.model_copy(update={"task_id": None})
                if bundle.tasks
                else bundle.trace
            )
            self._upsert_trace(cursor, provisional_trace)
            for task in bundle.tasks:
                self._upsert_task(cursor, task)
            self._upsert_trace(cursor, bundle.trace)
            for step in bundle.steps:
                self._upsert_step(cursor, step)
            for plan in bundle.plan_versions:
                self._upsert_plan_version(cursor, plan)
            for artifact in bundle.artifacts:
                self._upsert_artifact(cursor, artifact)
            for observation in bundle.observations:
                self._upsert_observation(cursor, observation)
            for delta in bundle.state_deltas:
                self._upsert_state_delta(cursor, delta)
            for snapshot in bundle.state_snapshots:
                self._upsert_state_snapshot(cursor, snapshot)
            for claim in bundle.claims:
                self._upsert_claim(cursor, claim)
            for edge in bundle.evidence_edges:
                self._upsert_evidence_edge(cursor, edge)
            for explanation in bundle.explanations:
                self._upsert_explanation(cursor, explanation)
            for evaluation in bundle.evaluations:
                self._upsert_evaluation(cursor, evaluation)
            for intervention in bundle.interventions:
                self._upsert_intervention(cursor, intervention)
            for policy in bundle.policies:
                self._upsert_policy(cursor, policy)
            for retention in bundle.retention:
                self._upsert_retention(cursor, retention)

        audit_event = self.record_audit_event(
            trace_id=bundle.trace.id,
            event_type="ingest.accepted",
            actor="api",
            outcome="recorded",
            metadata_json={
                "entity_counts": {
                    "tasks": len(bundle.tasks),
                    "plan_versions": len(bundle.plan_versions),
                    "state_snapshots": len(bundle.state_snapshots),
                    "steps": len(bundle.steps),
                    "observations": len(bundle.observations),
                    "state_deltas": len(bundle.state_deltas),
                    "artifacts": len(bundle.artifacts),
                    "claims": len(bundle.claims),
                    "explanations": len(bundle.explanations),
                    "evaluations": len(bundle.evaluations),
                    "interventions": len(bundle.interventions),
                }
            },
        )
        return IngestReceipt(
            session_id=bundle.session.id,
            trace_id=bundle.trace.id,
            entity_counts={
                "tasks": len(bundle.tasks),
                "plan_versions": len(bundle.plan_versions),
                "state_snapshots": len(bundle.state_snapshots),
                "steps": len(bundle.steps),
                "observations": len(bundle.observations),
                "state_deltas": len(bundle.state_deltas),
                "artifacts": len(bundle.artifacts),
                "claims": len(bundle.claims),
                "explanations": len(bundle.explanations),
                "evaluations": len(bundle.evaluations),
                "interventions": len(bundle.interventions),
            },
            audit_event_id=audit_event.id,
        )

    def build_timeline(self, trace_id: UUID) -> list[TimelineEntryView]:
        bundle = self.get_trace_bundle(trace_id)
        return [] if bundle is None else build_timeline(bundle)

    def build_state_diffs(self, trace_id: UUID) -> list[StateDiffEntryView]:
        bundle = self.get_trace_bundle(trace_id)
        return [] if bundle is None else build_state_diffs(bundle)

    def build_claim_flows(self, trace_id: UUID) -> list[ClaimEvidenceFlowView]:
        bundle = self.get_trace_bundle(trace_id)
        return [] if bundle is None else build_claim_flows(bundle)

    def build_replay(self, trace_id: UUID) -> list[ReplayFrameView]:
        bundle = self.get_trace_bundle(trace_id)
        return [] if bundle is None else build_replay(bundle)

    def get_task_state(self, trace_id: UUID) -> TaskStateView | None:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return None
        return build_task_state_view(bundle)

    def list_plan_versions(self, trace_id: UUID) -> list[PlanVersionRecord]:
        bundle = self.get_trace_bundle(trace_id)
        return (
            []
            if bundle is None
            else sorted(bundle.plan_versions, key=lambda item: item.revision)
        )

    def list_state_snapshots(self, trace_id: UUID) -> list[StateSnapshotRecord]:
        bundle = self.get_trace_bundle(trace_id)
        return (
            []
            if bundle is None
            else sorted(bundle.state_snapshots, key=lambda item: item.snapshot_index)
        )

    def upsert_research_documents(
        self,
        source_type: str,
        response: ResearchSearchResponse,
        cursor: str | None = None,
        metadata_json: dict[str, object] | None = None,
    ) -> ResearchSyncReceipt:
        sync_run = ResearchSyncRunRecord(
            id=uuid4(),
            source_type=source_type,
            query=response.query,
            cursor=cursor,
            status="completed",
            item_count=len(response.items),
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            metadata_json=metadata_json or {},
        )
        with self._connect() as connection:
            cursor_handle = connection.cursor()
            self._upsert_research_sync_run(cursor_handle, sync_run)
            for item in response.items:
                persisted_item = item.model_copy(
                    update={
                        "provenance": item.provenance.model_copy(
                            update={
                                "query": response.query,
                                "cursor": cursor,
                            }
                        )
                    }
                )
                self._upsert_research_document(cursor_handle, persisted_item, sync_run.id)
            if cursor is not None:
                self._upsert_research_cursor(
                    cursor_handle,
                    ResearchSyncCursorRecord(
                        source_type=source_type,
                        cursor_key="default",
                        cursor_value=cursor,
                        updated_at=datetime.now(UTC),
                        metadata_json=metadata_json or {},
                    ),
                )
        return ResearchSyncReceipt(
            sync_run_id=sync_run.id,
            source_type=source_type,
            query=response.query,
            cursor=cursor,
            item_count=len(response.items),
            upserted_count=len(response.items),
        )

    def list_research_documents(
        self,
        source_type: str | None = None,
        query: str = "",
    ) -> ResearchCorpusView:
        conditions: list[str] = []
        params: list[Any] = []
        if source_type is not None:
            conditions.append("source_type = %s")
            params.append(source_type)
        if query.strip():
            pattern = f"%{query.strip().lower()}%"
            conditions.append(
                "("
                "lower(title) like %s or lower(summary) like %s "
                "or exists ("
                "select 1 from jsonb_array_elements_text(tags) as tag "
                "where lower(tag) like %s"
                ")"
                ")"
            )
            params.extend([pattern, pattern, pattern])
        where_clause = f"where {' and '.join(conditions)}" if conditions else ""
        rows = self._fetch_all(
            f"""
            select *
            from research_documents
            {where_clause}
            order by retrieved_at desc, title asc
            """,
            params,
        )
        items = [self._research_document_from_row(row) for row in rows]
        return ResearchCorpusView(query=query, source_type=source_type, items=items)

    def list_research_sync_runs(
        self,
        source_type: str | None = None,
    ) -> list[ResearchSyncRunRecord]:
        if source_type is None:
            rows = self._fetch_all(
                "select * from research_sync_runs order by started_at desc",
                [],
            )
        else:
            rows = self._fetch_all(
                """
                select * from research_sync_runs
                where source_type = %s
                order by started_at desc
                """,
                [source_type],
            )
        return [self._model(ResearchSyncRunRecord, row) for row in rows]

    def get_research_cursor(
        self,
        source_type: str,
        cursor_key: str = "default",
    ) -> ResearchSyncCursorRecord | None:
        row = self._fetch_one(
            """
            select * from research_sync_cursors
            where source_type = %s and cursor_key = %s
            """,
            [source_type, cursor_key],
        )
        return None if row is None else self._model(ResearchSyncCursorRecord, row)

    def list_audit_events(self, trace_id: UUID | None = None) -> list[AuditEventRecord]:
        if trace_id is None:
            rows = self._fetch_all("select * from audit_events order by occurred_at", [])
        else:
            rows = self._fetch_all(
                "select * from audit_events where trace_id = %s::uuid order by occurred_at",
                [str(trace_id)],
            )
        return [self._model(AuditEventRecord, row) for row in rows]

    def list_policies(self) -> list[PolicyRuleRecord]:
        return self._fetch_models(
            PolicyRuleRecord,
            "select * from policy_rules order by name",
            [],
        )

    def list_retention(self) -> list[RetentionPolicyRecord]:
        return self._fetch_models(
            RetentionPolicyRecord,
            "select * from retention_policies order by name",
            [],
        )

    def record_audit_event(
        self,
        trace_id: UUID | None,
        event_type: str,
        actor: str,
        outcome: str,
        metadata_json: dict[str, object] | None = None,
    ) -> AuditEventRecord:
        event = AuditEventRecord(
            id=uuid4(),
            trace_id=trace_id,
            event_type=event_type,
            actor=actor,
            outcome=outcome,
            occurred_at=datetime.now(UTC),
            metadata_json=metadata_json or {},
        )
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                insert into audit_events (
                    id, trace_id, event_type, actor, outcome, occurred_at, metadata_json
                ) values (
                    %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb
                )
                on conflict (id) do nothing
                """,
                [
                    str(event.id),
                    str(event.trace_id) if event.trace_id is not None else None,
                    event.event_type,
                    event.actor,
                    event.outcome,
                    event.occurred_at,
                    json.dumps(event.metadata_json),
                ],
            )
        return event

    def _list_trace_ids(self) -> list[UUID]:
        rows = self._fetch_all("select id from traces order by started_at", [])
        return [UUID(str(row["id"])) for row in rows]

    def _fetch_models(
        self,
        model_cls: Any,
        query: str,
        params: list[Any],
        empty_on: list[Any] | None = None,
    ) -> list[Any]:
        if empty_on is not None and any(param == [] for param in params):
            return empty_on
        return [self._model(model_cls, row) for row in self._fetch_all(query, params)]

    def _fetch_one(self, query: str, params: list[Any]) -> dict[str, Any] | None:
        rows = self._fetch_all(query, params)
        return rows[0] if rows else None

    def _fetch_all(self, query: str, params: list[Any]) -> list[dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [item[0] for item in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows]

    def _model(self, model_cls: Any, row: dict[str, Any]) -> Any:
        normalized = {
            key: self._decode_json(value)
            for key, value in row.items()
        }
        return model_cls.model_validate(normalized)

    def _decode_json(self, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        return value

    def _research_document_from_row(self, row: dict[str, Any]) -> ResearchDocumentRecord:
        normalized = {key: self._decode_json(value) for key, value in row.items()}
        return ResearchDocumentRecord.model_validate(
            {
                "id": normalized["id"],
                "title": normalized["title"],
                "summary": normalized["summary"],
                "authors": normalized.get("authors", []),
                "published_at": normalized.get("published_at"),
                "mime_type": normalized.get("mime_type"),
                "content_ref": normalized.get("content_ref"),
                "tags": normalized.get("tags", []),
                "provenance": {
                    "source_type": normalized["source_type"],
                    "source_id": normalized["source_id"],
                    "source_uri": normalized["source_uri"],
                    "retrieved_at": normalized["retrieved_at"],
                    "query": normalized.get("query", ""),
                    "cursor": normalized.get("cursor"),
                    "license_or_terms_note": normalized.get("license_or_terms_note"),
                    "checksum": normalized.get("checksum"),
                    "export_status": normalized.get("export_status"),
                    "metadata_json": normalized.get("metadata_json", {}),
                },
            }
        )

    def _upsert_session(self, cursor: Any, session: SessionRecord) -> None:
        cursor.execute(
            """
            insert into sessions (
                id, source, user_id, project_id, external_conversation_id, started_at,
                ended_at, status, metadata_json, labels_jsonb, created_at
            ) values (
                %s::uuid, %s, %s, %s::uuid, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s
            )
            on conflict (id) do update set
                source = excluded.source,
                user_id = excluded.user_id,
                project_id = excluded.project_id,
                external_conversation_id = excluded.external_conversation_id,
                started_at = excluded.started_at,
                ended_at = excluded.ended_at,
                status = excluded.status,
                metadata_json = excluded.metadata_json,
                labels_jsonb = excluded.labels_jsonb
            """,
            [
                str(session.id),
                session.source,
                session.user_id,
                str(session.project_id) if session.project_id is not None else None,
                session.external_conversation_id,
                session.started_at,
                session.ended_at,
                session.status.value,
                json.dumps(session.metadata_json),
                json.dumps(session.labels_jsonb),
                session.created_at,
            ],
        )

    def _upsert_task(self, cursor: Any, task: TaskRecord) -> None:
        cursor.execute(
            """
            insert into tasks (
                id, session_id, trace_id, title, status, owner, summary, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                session_id = excluded.session_id,
                trace_id = excluded.trace_id,
                title = excluded.title,
                status = excluded.status,
                owner = excluded.owner,
                summary = excluded.summary,
                metadata_json = excluded.metadata_json
            """,
            [
                str(task.id),
                str(task.session_id),
                str(task.trace_id),
                task.title,
                task.status.value,
                task.owner,
                task.summary,
                json.dumps(task.metadata_json),
                task.created_at,
            ],
        )

    def _upsert_trace(self, cursor: Any, trace: Any) -> None:
        cursor.execute(
            """
            insert into traces (
                id, session_id, parent_trace_id, task_id, model_name, trace_kind,
                started_at, ended_at,
                status, config_ref, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                session_id = excluded.session_id,
                parent_trace_id = excluded.parent_trace_id,
                task_id = excluded.task_id,
                model_name = excluded.model_name,
                trace_kind = excluded.trace_kind,
                started_at = excluded.started_at,
                ended_at = excluded.ended_at,
                status = excluded.status,
                config_ref = excluded.config_ref,
                metadata_json = excluded.metadata_json
            """,
            [
                str(trace.id),
                str(trace.session_id),
                str(trace.parent_trace_id) if trace.parent_trace_id is not None else None,
                str(trace.task_id) if trace.task_id is not None else None,
                trace.model_name,
                trace.trace_kind,
                trace.started_at,
                trace.ended_at,
                trace.status.value,
                trace.config_ref,
                json.dumps(trace.metadata_json),
                trace.created_at,
            ],
        )

    def _upsert_plan_version(self, cursor: Any, plan: PlanVersionRecord) -> None:
        cursor.execute(
            """
            insert into plan_versions (
                id, task_id, trace_id, step_id, revision, summary,
                plan_json, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s::uuid, %s, %s, %s::jsonb, %s::jsonb, %s
            )
            on conflict (id) do update set
                task_id = excluded.task_id,
                trace_id = excluded.trace_id,
                step_id = excluded.step_id,
                revision = excluded.revision,
                summary = excluded.summary,
                plan_json = excluded.plan_json,
                metadata_json = excluded.metadata_json
            """,
            [
                str(plan.id),
                str(plan.task_id),
                str(plan.trace_id),
                str(plan.step_id) if plan.step_id is not None else None,
                plan.revision,
                plan.summary,
                json.dumps(plan.plan_json),
                json.dumps(plan.metadata_json),
                plan.created_at,
            ],
        )

    def _upsert_step(self, cursor: Any, step: StepRecord) -> None:
        cursor.execute(
            """
            insert into steps (
                id, trace_id, parent_step_id, step_index, step_type, actor, started_at, ended_at,
                status, summary, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                trace_id = excluded.trace_id,
                parent_step_id = excluded.parent_step_id,
                step_index = excluded.step_index,
                step_type = excluded.step_type,
                actor = excluded.actor,
                started_at = excluded.started_at,
                ended_at = excluded.ended_at,
                status = excluded.status,
                summary = excluded.summary,
                metadata_json = excluded.metadata_json
            """,
            [
                str(step.id),
                str(step.trace_id),
                str(step.parent_step_id) if step.parent_step_id is not None else None,
                step.step_index,
                step.step_type,
                step.actor,
                step.started_at,
                step.ended_at,
                step.status.value,
                step.summary,
                json.dumps(step.metadata_json),
                step.created_at,
            ],
        )

    def _upsert_observation(self, cursor: Any, observation: ObservationRecord) -> None:
        cursor.execute(
            """
            insert into observations (
                id, step_id, kind, content_ref, confidence, source_artifact_id,
                metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s, %s, %s, %s::uuid, %s::jsonb, %s
            )
            on conflict (id) do update set
                step_id = excluded.step_id,
                kind = excluded.kind,
                content_ref = excluded.content_ref,
                confidence = excluded.confidence,
                source_artifact_id = excluded.source_artifact_id,
                metadata_json = excluded.metadata_json
            """,
            [
                str(observation.id),
                str(observation.step_id),
                observation.kind,
                observation.content_ref,
                observation.confidence,
                str(observation.source_artifact_id)
                if observation.source_artifact_id is not None
                else None,
                json.dumps(observation.metadata_json),
                observation.created_at,
            ],
        )

    def _upsert_state_delta(self, cursor: Any, delta: StateDeltaRecord) -> None:
        cursor.execute(
            """
            insert into state_deltas (
                id, step_id, facet, before_json, after_json, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s
            )
            on conflict (id) do update set
                step_id = excluded.step_id,
                facet = excluded.facet,
                before_json = excluded.before_json,
                after_json = excluded.after_json,
                metadata_json = excluded.metadata_json
            """,
            [
                str(delta.id),
                str(delta.step_id),
                delta.facet,
                json.dumps(delta.before_json),
                json.dumps(delta.after_json),
                json.dumps(delta.metadata_json),
                delta.created_at,
            ],
        )

    def _upsert_state_snapshot(self, cursor: Any, snapshot: StateSnapshotRecord) -> None:
        cursor.execute(
            """
            insert into state_snapshots (
                id, trace_id, step_id, task_id, snapshot_index,
                state_json, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s::uuid, %s, %s::jsonb, %s::jsonb, %s
            )
            on conflict (id) do update set
                trace_id = excluded.trace_id,
                step_id = excluded.step_id,
                task_id = excluded.task_id,
                snapshot_index = excluded.snapshot_index,
                state_json = excluded.state_json,
                metadata_json = excluded.metadata_json
            """,
            [
                str(snapshot.id),
                str(snapshot.trace_id),
                str(snapshot.step_id) if snapshot.step_id is not None else None,
                str(snapshot.task_id) if snapshot.task_id is not None else None,
                snapshot.snapshot_index,
                json.dumps(snapshot.state_json),
                json.dumps(snapshot.metadata_json),
                snapshot.created_at,
            ],
        )

    def _upsert_artifact(self, cursor: Any, artifact: ArtifactRecord) -> None:
        cursor.execute(
            """
            insert into artifacts (
                id, source_type, source_system, source_uri, mime_type, checksum, storage_ref,
                metadata_json, created_at
            ) values (
                %s::uuid, %s, %s, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                source_type = excluded.source_type,
                source_system = excluded.source_system,
                source_uri = excluded.source_uri,
                mime_type = excluded.mime_type,
                checksum = excluded.checksum,
                storage_ref = excluded.storage_ref,
                metadata_json = excluded.metadata_json
            """,
            [
                str(artifact.id),
                artifact.source_type,
                artifact.source_system,
                artifact.source_uri,
                artifact.mime_type,
                artifact.checksum,
                artifact.storage_ref,
                json.dumps(artifact.metadata_json),
                artifact.created_at,
            ],
        )

    def _upsert_claim(self, cursor: Any, claim: Any) -> None:
        cursor.execute(
            """
            insert into claims (
                id, trace_id, claim_text, claim_type, confidence, position_index,
                verification_status, metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                trace_id = excluded.trace_id,
                claim_text = excluded.claim_text,
                claim_type = excluded.claim_type,
                confidence = excluded.confidence,
                position_index = excluded.position_index,
                verification_status = excluded.verification_status,
                metadata_json = excluded.metadata_json
            """,
            [
                str(claim.id),
                str(claim.trace_id),
                claim.claim_text,
                claim.claim_type,
                claim.confidence,
                claim.position_index,
                claim.verification_status.value,
                json.dumps(claim.metadata_json),
                claim.created_at,
            ],
        )

    def _upsert_evidence_edge(self, cursor: Any, edge: EvidenceEdgeRecord) -> None:
        cursor.execute(
            """
            insert into evidence_edges (
                id, from_kind, from_id, to_kind, to_id, relation, weight, metadata_json, created_at
            ) values (
                %s::uuid, %s, %s::uuid, %s, %s::uuid, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                from_kind = excluded.from_kind,
                from_id = excluded.from_id,
                to_kind = excluded.to_kind,
                to_id = excluded.to_id,
                relation = excluded.relation,
                weight = excluded.weight,
                metadata_json = excluded.metadata_json
            """,
            [
                str(edge.id),
                edge.from_kind.value,
                str(edge.from_id),
                edge.to_kind.value,
                str(edge.to_id),
                edge.relation,
                edge.weight,
                json.dumps(edge.metadata_json),
                edge.created_at,
            ],
        )

    def _upsert_explanation(self, cursor: Any, explanation: ExplanationRecord) -> None:
        cursor.execute(
            """
            insert into explanation_records (
                id, claim_id, grade, method, summary, supporting_edge_ids, confidence,
                metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                claim_id = excluded.claim_id,
                grade = excluded.grade,
                method = excluded.method,
                summary = excluded.summary,
                supporting_edge_ids = excluded.supporting_edge_ids,
                confidence = excluded.confidence,
                metadata_json = excluded.metadata_json
            """,
            [
                str(explanation.id),
                str(explanation.claim_id),
                explanation.grade.value,
                explanation.method,
                explanation.summary,
                [str(item) for item in explanation.supporting_edge_ids],
                explanation.confidence,
                json.dumps(explanation.metadata_json),
                explanation.created_at,
            ],
        )

    def _upsert_evaluation(self, cursor: Any, evaluation: EvaluationRecord) -> None:
        cursor.execute(
            """
            insert into evaluations (
                id, trace_id, suite_name, metric_name, score, verdict, details_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                trace_id = excluded.trace_id,
                suite_name = excluded.suite_name,
                metric_name = excluded.metric_name,
                score = excluded.score,
                verdict = excluded.verdict,
                details_json = excluded.details_json
            """,
            [
                str(evaluation.id),
                str(evaluation.trace_id),
                evaluation.suite_name,
                evaluation.metric_name,
                evaluation.score,
                evaluation.verdict,
                json.dumps(evaluation.details_json),
                evaluation.created_at,
            ],
        )

    def _upsert_intervention(self, cursor: Any, intervention: InterventionRecord) -> None:
        cursor.execute(
            """
            insert into interventions (
                id, trace_id, step_id, intervention_type, reason, actor, result,
                metadata_json, created_at
            ) values (
                %s::uuid, %s::uuid, %s::uuid, %s, %s, %s, %s, %s::jsonb, %s
            )
            on conflict (id) do update set
                trace_id = excluded.trace_id,
                step_id = excluded.step_id,
                intervention_type = excluded.intervention_type,
                reason = excluded.reason,
                actor = excluded.actor,
                result = excluded.result,
                metadata_json = excluded.metadata_json
            """,
            [
                str(intervention.id),
                str(intervention.trace_id),
                str(intervention.step_id) if intervention.step_id is not None else None,
                intervention.intervention_type,
                intervention.reason,
                intervention.actor,
                intervention.result,
                json.dumps(intervention.metadata_json),
                intervention.created_at,
            ],
        )

    def _upsert_policy(self, cursor: Any, policy: PolicyRuleRecord) -> None:
        cursor.execute(
            """
            insert into policy_rules (
                id, name, category, mode, applies_to, description, configured_by, metadata_json
            ) values (
                %s::uuid, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb
            )
            on conflict (id) do update set
                name = excluded.name,
                category = excluded.category,
                mode = excluded.mode,
                applies_to = excluded.applies_to,
                description = excluded.description,
                configured_by = excluded.configured_by,
                metadata_json = excluded.metadata_json
            """,
            [
                str(policy.id),
                policy.name,
                policy.category,
                policy.mode,
                json.dumps(policy.applies_to),
                policy.description,
                policy.configured_by,
                json.dumps(policy.metadata_json),
            ],
        )

    def _upsert_retention(self, cursor: Any, retention: RetentionPolicyRecord) -> None:
        cursor.execute(
            """
            insert into retention_policies (
                id, name, applies_to, retention_days, purge_strategy, redaction_scope, metadata_json
            ) values (
                %s::uuid, %s, %s::jsonb, %s, %s, %s::jsonb, %s::jsonb
            )
            on conflict (id) do update set
                name = excluded.name,
                applies_to = excluded.applies_to,
                retention_days = excluded.retention_days,
                purge_strategy = excluded.purge_strategy,
                redaction_scope = excluded.redaction_scope,
                metadata_json = excluded.metadata_json
            """,
            [
                str(retention.id),
                retention.name,
                json.dumps(retention.applies_to),
                retention.retention_days,
                retention.purge_strategy,
                json.dumps(retention.redaction_scope),
                json.dumps(retention.metadata_json),
            ],
        )

    def _upsert_research_sync_run(self, cursor: Any, sync_run: ResearchSyncRunRecord) -> None:
        cursor.execute(
            """
            insert into research_sync_runs (
                id, source_type, query, cursor, status, item_count,
                started_at, completed_at, metadata_json
            ) values (
                %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
            )
            on conflict (id) do update set
                source_type = excluded.source_type,
                query = excluded.query,
                cursor = excluded.cursor,
                status = excluded.status,
                item_count = excluded.item_count,
                started_at = excluded.started_at,
                completed_at = excluded.completed_at,
                metadata_json = excluded.metadata_json
            """,
            [
                str(sync_run.id),
                sync_run.source_type,
                sync_run.query,
                sync_run.cursor,
                sync_run.status,
                sync_run.item_count,
                sync_run.started_at,
                sync_run.completed_at,
                json.dumps(sync_run.metadata_json),
            ],
        )

    def _upsert_research_cursor(
        self,
        cursor: Any,
        record: ResearchSyncCursorRecord,
    ) -> None:
        cursor.execute(
            """
            insert into research_sync_cursors (
                source_type, cursor_key, cursor_value, updated_at, metadata_json
            ) values (
                %s, %s, %s, %s, %s::jsonb
            )
            on conflict (source_type, cursor_key) do update set
                cursor_value = excluded.cursor_value,
                updated_at = excluded.updated_at,
                metadata_json = excluded.metadata_json
            """,
            [
                record.source_type,
                record.cursor_key,
                record.cursor_value,
                record.updated_at,
                json.dumps(record.metadata_json),
            ],
        )

    def _upsert_research_document(
        self,
        cursor: Any,
        item: ResearchDocumentRecord,
        sync_run_id: UUID,
    ) -> None:
        cursor.execute(
            """
            insert into research_documents (
                id, source_type, source_id, source_uri, title, summary, authors,
                published_at, mime_type, content_ref, tags, retrieved_at, query, cursor,
                license_or_terms_note, checksum, export_status, sync_run_id, metadata_json
            ) values (
                %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, %s, %s, %s,
                %s, %s, %s, %s::uuid, %s::jsonb
            )
            on conflict (id) do update set
                source_type = excluded.source_type,
                source_id = excluded.source_id,
                source_uri = excluded.source_uri,
                title = excluded.title,
                summary = excluded.summary,
                authors = excluded.authors,
                published_at = excluded.published_at,
                mime_type = excluded.mime_type,
                content_ref = excluded.content_ref,
                tags = excluded.tags,
                retrieved_at = excluded.retrieved_at,
                query = excluded.query,
                cursor = excluded.cursor,
                license_or_terms_note = excluded.license_or_terms_note,
                checksum = excluded.checksum,
                export_status = excluded.export_status,
                sync_run_id = excluded.sync_run_id,
                metadata_json = excluded.metadata_json
            """,
            [
                item.id,
                item.provenance.source_type,
                item.provenance.source_id,
                item.provenance.source_uri,
                item.title,
                item.summary,
                json.dumps(item.authors),
                item.published_at,
                item.mime_type,
                item.content_ref,
                json.dumps(item.tags),
                item.provenance.retrieved_at,
                item.provenance.query,
                item.provenance.cursor,
                item.provenance.license_or_terms_note,
                item.provenance.checksum,
                item.provenance.export_status,
                str(sync_run_id),
                json.dumps(item.provenance.metadata_json),
            ],
        )
