from __future__ import annotations

from typing import Iterable
from uuid import UUID

from packages.schema.flight_recorder_schema import (
    ArtifactRecord,
    AuditEventRecord,
    ClaimEvidenceFlowView,
    ClaimVerificationStatus,
    EntityKind,
    EvidenceGrade,
    ReplayFrameView,
    StateDiffEntryView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)

GRADE_PRIORITY = {
    EvidenceGrade.SELF_REPORTED: 1,
    EvidenceGrade.INFERRED: 2,
    EvidenceGrade.OBSERVED: 3,
    EvidenceGrade.VERIFIED: 4,
}


def build_trace_summaries(
    bundles: Iterable[TraceBundleView],
    audit_lookup: dict[UUID, list[AuditEventRecord]] | None = None,
) -> list[TraceSummaryView]:
    summaries: list[TraceSummaryView] = []
    audit_lookup = audit_lookup or {}

    for bundle in bundles:
        trace = bundle.trace
        claims = bundle.claims
        audit_events = audit_lookup.get(trace.id, bundle.audit_events)
        summaries.append(
            TraceSummaryView(
                trace_id=trace.id,
                session_id=trace.session_id,
                status=trace.status,
                model_name=trace.model_name,
                trace_kind=trace.trace_kind,
                started_at=trace.started_at,
                ended_at=trace.ended_at,
                step_count=len(bundle.steps),
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


def build_timeline(bundle: TraceBundleView) -> list[TimelineEntryView]:
    timeline: list[TimelineEntryView] = []

    for step in bundle.steps:
        observations = [item for item in bundle.observations if item.step_id == step.id]
        claim_ids = claim_ids_for_step(bundle, step.id)
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


def build_state_diffs(bundle: TraceBundleView) -> list[StateDiffEntryView]:
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


def build_claim_flows(bundle: TraceBundleView) -> list[ClaimEvidenceFlowView]:
    flows: list[ClaimEvidenceFlowView] = []

    for claim in bundle.claims:
        edges = [
            edge
            for edge in bundle.evidence_edges
            if edge.from_kind == EntityKind.CLAIM and edge.from_id == claim.id
        ]
        artifact_ids = [edge.to_id for edge in edges if edge.to_kind == EntityKind.ARTIFACT]
        step_ids = [edge.to_id for edge in edges if edge.to_kind == EntityKind.STEP]
        artifacts = [artifact for artifact in bundle.artifacts if artifact.id in set(artifact_ids)]
        explanations = [
            explanation for explanation in bundle.explanations if explanation.claim_id == claim.id
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


def build_replay(bundle: TraceBundleView) -> list[ReplayFrameView]:
    frames: list[ReplayFrameView] = []

    for index, step in enumerate(bundle.steps):
        claim_ids = claim_ids_for_step(bundle, step.id)
        frames.append(
            ReplayFrameView(
                frame_index=index,
                step=step,
                observations=[item for item in bundle.observations if item.step_id == step.id],
                state_deltas=[item for item in bundle.state_deltas if item.step_id == step.id],
                claims=[claim for claim in bundle.claims if claim.id in claim_ids],
                interventions=[item for item in bundle.interventions if item.step_id == step.id],
            )
        )

    return frames


def artifacts_for_trace(bundle: TraceBundleView) -> list[ArtifactRecord]:
    artifact_ids = {
        observation.source_artifact_id
        for observation in bundle.observations
        if observation.source_artifact_id is not None
    }
    artifact_ids.update(
        {
            edge.to_id
            for edge in bundle.evidence_edges
            if edge.to_kind == EntityKind.ARTIFACT
        }
    )
    return sorted(
        [artifact for artifact in bundle.artifacts if artifact.id in artifact_ids],
        key=lambda artifact: artifact.id,
    )


def claim_ids_for_step(bundle: TraceBundleView, step_id: UUID) -> list[UUID]:
    claim_ids = {
        edge.from_id
        for edge in bundle.evidence_edges
        if edge.from_kind == EntityKind.CLAIM
        and edge.to_kind == EntityKind.STEP
        and edge.to_id == step_id
    }
    return sorted(claim_ids, key=str)
