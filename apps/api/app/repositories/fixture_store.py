from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from apps.api.app.cognitive import build_task_state_view, ensure_cognitive_state
from apps.api.app.why import ensure_why_records
from packages.schema.flight_recorder_schema import (
    ArtifactRecord,
    AuditEventRecord,
    ClaimEvidenceFlowView,
    EntityKind,
    ExplanationRecord,
    IngestReceipt,
    PlanVersionRecord,
    ReplayFrameView,
    ResearchCorpusView,
    ResearchDocumentRecord,
    ResearchSearchResponse,
    ResearchSyncCursorRecord,
    ResearchSyncReceipt,
    ResearchSyncRunRecord,
    RetentionPolicyRecord,
    StateDiffEntryView,
    StateSnapshotRecord,
    TaskStateView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)
from packages.testkit import load_trace_bundle_fixture

from .helpers import (
    build_claim_flows,
    build_replay,
    build_state_diffs,
    build_timeline,
    build_trace_summaries,
)


class FixtureTraceRepository:
    def __init__(self, seed: TraceBundleView) -> None:
        seed = ensure_cognitive_state(seed)
        seed = ensure_why_records(seed)
        self._sessions = {seed.session.id: seed.session}
        self._traces = {seed.trace.id: seed.trace}
        self._tasks = {task.id: task for task in seed.tasks}
        self._plan_versions = {plan.id: plan for plan in seed.plan_versions}
        self._state_snapshots = {snapshot.id: snapshot for snapshot in seed.state_snapshots}
        self._steps = {step.id: step for step in seed.steps}
        self._observations = {observation.id: observation for observation in seed.observations}
        self._state_deltas = {delta.id: delta for delta in seed.state_deltas}
        self._artifacts = {artifact.id: artifact for artifact in seed.artifacts}
        self._evidence_edges = {edge.id: edge for edge in seed.evidence_edges}
        self._claims = {claim.id: claim for claim in seed.claims}
        self._explanations = {explanation.id: explanation for explanation in seed.explanations}
        self._evaluations = {evaluation.id: evaluation for evaluation in seed.evaluations}
        self._interventions = {
            intervention.id: intervention for intervention in seed.interventions
        }
        self._audit_events = {event.id: event for event in seed.audit_events}
        self._policies = {policy.id: policy for policy in seed.policies}
        self._retention = {policy.id: policy for policy in seed.retention}
        self._research_documents: dict[str, ResearchDocumentRecord] = {}
        self._research_sync_runs: dict[UUID, ResearchSyncRunRecord] = {}
        self._research_cursors: dict[tuple[str, str], ResearchSyncCursorRecord] = {}

    @classmethod
    def seeded(cls) -> "FixtureTraceRepository":
        return cls(load_trace_bundle_fixture())

    def list_traces(self) -> list[TraceSummaryView]:
        bundles = [self.get_trace_bundle(trace_id) for trace_id in self._traces]
        return build_trace_summaries(
            [bundle for bundle in bundles if bundle is not None],
            {trace_id: self.list_audit_events(trace_id) for trace_id in self._traces},
        )

    def get_trace_bundle(self, trace_id: UUID) -> TraceBundleView | None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return None

        session = self._sessions[trace.session_id]

        return TraceBundleView(
            session=session,
            trace=trace,
            tasks=self._tasks_for_trace(trace_id),
            plan_versions=self.list_plan_versions(trace_id),
            state_snapshots=self.list_state_snapshots(trace_id),
            steps=self._steps_for_trace(trace_id),
            observations=self._observations_for_trace(trace_id),
            state_deltas=self._state_deltas_for_trace(trace_id),
            artifacts=self._artifacts_for_trace(trace_id),
            evidence_edges=self._edges_for_trace(trace_id),
            claims=self._claims_for_trace(trace_id),
            explanations=self._explanations_for_trace(trace_id),
            evaluations=self._evaluations_for_trace(trace_id),
            interventions=self._interventions_for_trace(trace_id),
            audit_events=self.list_audit_events(trace_id),
            policies=self.list_policies(),
            retention=self.list_retention(),
        )

    def upsert_bundle(self, bundle: TraceBundleView) -> IngestReceipt:
        bundle = ensure_cognitive_state(bundle)
        bundle = ensure_why_records(bundle)
        self._sessions[bundle.session.id] = bundle.session
        self._traces[bundle.trace.id] = bundle.trace

        for collection, target in [
            (bundle.tasks, self._tasks),
            (bundle.plan_versions, self._plan_versions),
            (bundle.state_snapshots, self._state_snapshots),
            (bundle.steps, self._steps),
            (bundle.observations, self._observations),
            (bundle.state_deltas, self._state_deltas),
            (bundle.artifacts, self._artifacts),
            (bundle.evidence_edges, self._evidence_edges),
            (bundle.claims, self._claims),
            (bundle.explanations, self._explanations),
            (bundle.evaluations, self._evaluations),
            (bundle.interventions, self._interventions),
        ]:
            for item in collection:
                target[item.id] = item

        for policy in bundle.policies:
            self._policies[policy.id] = policy
        for retention_policy in bundle.retention:
            self._retention[retention_policy.id] = retention_policy

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
        if bundle is None:
            return []
        return build_timeline(bundle)

    def build_state_diffs(self, trace_id: UUID) -> list[StateDiffEntryView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []
        return build_state_diffs(bundle)

    def build_claim_flows(self, trace_id: UUID) -> list[ClaimEvidenceFlowView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []
        return build_claim_flows(bundle)

    def build_replay(self, trace_id: UUID) -> list[ReplayFrameView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []
        return build_replay(bundle)

    def get_task_state(self, trace_id: UUID) -> TaskStateView | None:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return None
        return build_task_state_view(bundle)

    def list_plan_versions(self, trace_id: UUID) -> list[PlanVersionRecord]:
        task_ids = {task.id for task in self._tasks_for_trace(trace_id)}
        return sorted(
            [item for item in self._plan_versions.values() if item.task_id in task_ids],
            key=lambda item: item.revision,
        )

    def list_state_snapshots(self, trace_id: UUID) -> list[StateSnapshotRecord]:
        return sorted(
            [item for item in self._state_snapshots.values() if item.trace_id == trace_id],
            key=lambda item: item.snapshot_index,
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
        self._research_sync_runs[sync_run.id] = sync_run

        upserted_count = 0
        for item in response.items:
            cloned = item.model_copy(
                update={
                    "provenance": item.provenance.model_copy(
                        update={
                            "query": response.query,
                            "cursor": cursor,
                        }
                    )
                }
            )
            self._research_documents[item.id] = cloned
            upserted_count += 1

        if cursor is not None:
            self._research_cursors[(source_type, "default")] = ResearchSyncCursorRecord(
                source_type=source_type,
                cursor_key="default",
                cursor_value=cursor,
                updated_at=datetime.now(UTC),
                metadata_json=metadata_json or {},
            )

        return ResearchSyncReceipt(
            sync_run_id=sync_run.id,
            source_type=source_type,
            query=response.query,
            cursor=cursor,
            item_count=len(response.items),
            upserted_count=upserted_count,
        )

    def list_research_documents(
        self,
        source_type: str | None = None,
        query: str = "",
    ) -> ResearchCorpusView:
        tokens = [token.strip().lower() for token in query.split() if token.strip()]
        items = list(self._research_documents.values())
        if source_type is not None:
            items = [item for item in items if item.provenance.source_type == source_type]
        if tokens:
            items = [
                item
                for item in items
                if all(
                    token in " ".join([item.title, item.summary, *item.tags]).lower()
                    for token in tokens
                )
            ]
        items = sorted(items, key=lambda item: item.provenance.retrieved_at, reverse=True)
        return ResearchCorpusView(query=query, source_type=source_type, items=items)

    def list_research_sync_runs(
        self,
        source_type: str | None = None,
    ) -> list[ResearchSyncRunRecord]:
        runs = list(self._research_sync_runs.values())
        if source_type is not None:
            runs = [run for run in runs if run.source_type == source_type]
        return sorted(runs, key=lambda item: item.started_at, reverse=True)

    def get_research_cursor(
        self,
        source_type: str,
        cursor_key: str = "default",
    ) -> ResearchSyncCursorRecord | None:
        return self._research_cursors.get((source_type, cursor_key))

    def list_audit_events(self, trace_id: UUID | None = None) -> list[AuditEventRecord]:
        events = list(self._audit_events.values())
        if trace_id is not None:
            events = [event for event in events if event.trace_id == trace_id]
        return sorted(events, key=lambda item: item.occurred_at)

    def list_policies(self) -> list:
        return sorted(self._policies.values(), key=lambda item: item.name)

    def list_retention(self) -> list[RetentionPolicyRecord]:
        return sorted(self._retention.values(), key=lambda item: item.name)

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
        self._audit_events[event.id] = event
        return event

    def _steps_for_trace(self, trace_id: UUID) -> list:
        return sorted(
            [step for step in self._steps.values() if step.trace_id == trace_id],
            key=lambda item: item.step_index,
        )

    def _tasks_for_trace(self, trace_id: UUID) -> list:
        return sorted(
            [task for task in self._tasks.values() if task.trace_id == trace_id],
            key=lambda item: item.created_at,
        )

    def _observations_for_trace(self, trace_id: UUID) -> list:
        step_ids = {step.id for step in self._steps_for_trace(trace_id)}
        return sorted(
            [item for item in self._observations.values() if item.step_id in step_ids],
            key=lambda observation: observation.id,
        )

    def _state_deltas_for_trace(self, trace_id: UUID) -> list:
        step_ids = {step.id for step in self._steps_for_trace(trace_id)}
        return sorted(
            [item for item in self._state_deltas.values() if item.step_id in step_ids],
            key=lambda delta: (self._steps[delta.step_id].step_index, delta.facet),
        )

    def _claims_for_trace(self, trace_id: UUID) -> list:
        return sorted(
            [claim for claim in self._claims.values() if claim.trace_id == trace_id],
            key=lambda item: item.position_index,
        )

    def _explanations_for_trace(self, trace_id: UUID) -> list[ExplanationRecord]:
        claim_ids = {claim.id for claim in self._claims_for_trace(trace_id)}
        return sorted(
            [item for item in self._explanations.values() if item.claim_id in claim_ids],
            key=lambda explanation: explanation.id,
        )

    def _evaluations_for_trace(self, trace_id: UUID) -> list:
        return sorted(
            [item for item in self._evaluations.values() if item.trace_id == trace_id],
            key=lambda evaluation: evaluation.id,
        )

    def _interventions_for_trace(self, trace_id: UUID) -> list:
        return sorted(
            [
                item for item in self._interventions.values() if item.trace_id == trace_id
            ],
            key=lambda intervention: intervention.id,
        )

    def _edges_for_trace(self, trace_id: UUID) -> list:
        claim_ids = {claim.id for claim in self._claims_for_trace(trace_id)}
        step_ids = {step.id for step in self._steps_for_trace(trace_id)}
        artifact_ids = {
            observation.source_artifact_id
            for observation in self._observations_for_trace(trace_id)
            if observation.source_artifact_id is not None
        }
        return sorted(
            [
                edge
                for edge in self._evidence_edges.values()
                if (edge.from_kind == EntityKind.CLAIM and edge.from_id in claim_ids)
                or (edge.to_kind == EntityKind.STEP and edge.to_id in step_ids)
                or (edge.to_kind == EntityKind.ARTIFACT and edge.to_id in artifact_ids)
            ],
            key=lambda edge: edge.id,
        )

    def _artifacts_for_trace(self, trace_id: UUID) -> list[ArtifactRecord]:
        artifact_ids = {
            observation.source_artifact_id
            for observation in self._observations_for_trace(trace_id)
            if observation.source_artifact_id is not None
        }
        artifact_ids.update(
            {
                edge.to_id
                for edge in self._edges_for_trace(trace_id)
                if edge.to_kind == EntityKind.ARTIFACT
            }
        )
        return sorted(
            [artifact for artifact in self._artifacts.values() if artifact.id in artifact_ids],
            key=lambda artifact: artifact.id,
        )
