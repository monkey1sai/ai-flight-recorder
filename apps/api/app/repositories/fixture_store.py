from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from packages.schema.flight_recorder_schema import (
    ArtifactRecord,
    AuditEventRecord,
    ClaimEvidenceFlowView,
    ClaimVerificationStatus,
    EntityKind,
    EvidenceGrade,
    ExplanationRecord,
    IngestReceipt,
    ReplayFrameView,
    RetentionPolicyRecord,
    StateDiffEntryView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)
from packages.testkit import load_trace_bundle_fixture

GRADE_PRIORITY = {
    EvidenceGrade.SELF_REPORTED: 1,
    EvidenceGrade.INFERRED: 2,
    EvidenceGrade.OBSERVED: 3,
    EvidenceGrade.VERIFIED: 4,
}


class FixtureTraceRepository:
    def __init__(self, seed: TraceBundleView) -> None:
        self._sessions = {seed.session.id: seed.session}
        self._traces = {seed.trace.id: seed.trace}
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

    @classmethod
    def seeded(cls) -> "FixtureTraceRepository":
        return cls(load_trace_bundle_fixture())

    def list_traces(self) -> list[TraceSummaryView]:
        summaries: list[TraceSummaryView] = []

        for trace in self._traces.values():
            steps = self._steps_for_trace(trace.id)
            claims = self._claims_for_trace(trace.id)
            audit_events = self.list_audit_events(trace.id)

            summaries.append(
                TraceSummaryView(
                    trace_id=trace.id,
                    session_id=trace.session_id,
                    status=trace.status,
                    model_name=trace.model_name,
                    trace_kind=trace.trace_kind,
                    started_at=trace.started_at,
                    ended_at=trace.ended_at,
                    step_count=len(steps),
                    claim_count=len(claims),
                    unsupported_claim_count=sum(
                        1
                        for claim in claims
                        if claim.verification_status
                        in {
                            ClaimVerificationStatus.UNSUPPORTED,
                            ClaimVerificationStatus.MODEL_PRIOR_ONLY,
                            ClaimVerificationStatus.CONFLICTED,
                        }
                    ),
                    latest_audit_outcome=audit_events[-1].outcome if audit_events else None,
                )
            )

        return sorted(summaries, key=lambda item: item.started_at)

    def get_trace_bundle(self, trace_id: UUID) -> TraceBundleView | None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return None

        session = self._sessions[trace.session_id]

        return TraceBundleView(
            session=session,
            trace=trace,
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
        self._sessions[bundle.session.id] = bundle.session
        self._traces[bundle.trace.id] = bundle.trace

        for collection, target in [
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

        timeline: list[TimelineEntryView] = []

        for step in bundle.steps:
            observations = [item for item in bundle.observations if item.step_id == step.id]
            claim_ids = self._claim_ids_for_step(bundle, step.id)
            explanations = [item for item in bundle.explanations if item.claim_id in claim_ids]
            interventions = [item for item in bundle.interventions if item.step_id == step.id]

            artifact_ids = sorted(
                {
                    observation.source_artifact_id
                    for observation in observations
                    if observation.source_artifact_id is not None
                },
                key=str,
            )

            evidence_grade = max(
                (item.grade for item in explanations),
                key=lambda grade: GRADE_PRIORITY[grade],
                default=(
                    EvidenceGrade.OBSERVED
                    if observations
                    else EvidenceGrade.INFERRED if interventions else EvidenceGrade.SELF_REPORTED
                ),
            )

            timeline.append(
                TimelineEntryView(
                    step_id=step.id,
                    step_index=step.step_index,
                    step_type=step.step_type,
                    actor=step.actor,
                    status=step.status,
                    summary=step.summary,
                    started_at=step.started_at,
                    ended_at=step.ended_at,
                    evidence_grade=evidence_grade,
                    observation_count=len(observations),
                    artifact_ids=artifact_ids,
                    claim_ids=claim_ids,
                    intervention_ids=[item.id for item in interventions],
                )
            )

        return timeline

    def build_state_diffs(self, trace_id: UUID) -> list[StateDiffEntryView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []

        step_indexes = {step.id: step.step_index for step in bundle.steps}

        return [
            StateDiffEntryView(
                step_id=delta.step_id,
                step_index=step_indexes.get(delta.step_id, -1),
                facet=delta.facet,
                before_json=delta.before_json,
                after_json=delta.after_json,
                metadata_json=delta.metadata_json,
            )
            for delta in bundle.state_deltas
        ]

    def build_claim_flows(self, trace_id: UUID) -> list[ClaimEvidenceFlowView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []

        flows: list[ClaimEvidenceFlowView] = []

        for claim in bundle.claims:
            edges = [
                edge
                for edge in bundle.evidence_edges
                if edge.from_kind == EntityKind.CLAIM and edge.from_id == claim.id
            ]
            artifact_ids = [
                edge.to_id for edge in edges if edge.to_kind == EntityKind.ARTIFACT
            ]
            step_ids = [edge.to_id for edge in edges if edge.to_kind == EntityKind.STEP]
            artifacts = [
                artifact for artifact in bundle.artifacts if artifact.id in set(artifact_ids)
            ]
            explanations = [
                explanation
                for explanation in bundle.explanations
                if explanation.claim_id == claim.id
            ]
            flows.append(
                ClaimEvidenceFlowView(
                    claim=claim,
                    verification_status=claim.verification_status,
                    explanations=explanations,
                    supporting_edges=edges,
                    artifacts=artifacts,
                    supporting_step_ids=step_ids,
                )
            )

        return flows

    def build_replay(self, trace_id: UUID) -> list[ReplayFrameView]:
        bundle = self.get_trace_bundle(trace_id)
        if bundle is None:
            return []

        frames: list[ReplayFrameView] = []

        for index, step in enumerate(bundle.steps):
            claim_ids = self._claim_ids_for_step(bundle, step.id)
            frames.append(
                ReplayFrameView(
                    frame_index=index,
                    step=step,
                    observations=[
                        observation
                        for observation in bundle.observations
                        if observation.step_id == step.id
                    ],
                    state_deltas=[
                        delta for delta in bundle.state_deltas if delta.step_id == step.id
                    ],
                    claims=[claim for claim in bundle.claims if claim.id in claim_ids],
                    interventions=[
                        intervention
                        for intervention in bundle.interventions
                        if intervention.step_id == step.id
                    ],
                )
            )

        return frames

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

    def _claim_ids_for_step(self, bundle: TraceBundleView, step_id: UUID) -> list[UUID]:
        claim_ids = {
            edge.from_id
            for edge in bundle.evidence_edges
            if edge.from_kind == EntityKind.CLAIM
            and edge.to_kind == EntityKind.STEP
            and edge.to_id == step_id
        }
        return sorted(claim_ids, key=str)
