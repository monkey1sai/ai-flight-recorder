from datetime import UTC, datetime
from uuid import uuid4

from packages.schema.flight_recorder_schema import (
    ArtifactRecord,
    ClaimRecord,
    ClaimVerificationStatus,
    EntityKind,
    EvidenceEdgeRecord,
    EvidenceGrade,
    ExplanationRecord,
    SessionRecord,
    SessionStatus,
    StepRecord,
    StepStatus,
    TraceRecord,
    TraceStatus,
)


def test_canonical_models_share_enum_contract() -> None:
    session_id = uuid4()
    trace_id = uuid4()
    claim_id = uuid4()
    artifact_id = uuid4()
    edge_id = uuid4()
    timestamp = datetime.now(UTC)

    session = SessionRecord(
        id=session_id,
        source="codex",
        started_at=timestamp,
        status=SessionStatus.RUNNING,
    )
    trace = TraceRecord(
        id=trace_id,
        session_id=session_id,
        started_at=timestamp,
        status=TraceStatus.RUNNING,
    )
    step = StepRecord(
        id=uuid4(),
        trace_id=trace_id,
        step_index=0,
        step_type="tool_call",
        actor="agent",
        started_at=timestamp,
        status=StepStatus.COMPLETED,
    )
    artifact = ArtifactRecord(
        id=artifact_id,
        source_type="tool_result",
        storage_ref="s3://bucket/result.json",
    )
    claim = ClaimRecord(
        id=claim_id,
        trace_id=trace_id,
        claim_text="A supported factual claim.",
        claim_type="factual",
        position_index=0,
        verification_status=ClaimVerificationStatus.SUPPORTED,
    )
    edge = EvidenceEdgeRecord(
        id=edge_id,
        from_kind=EntityKind.CLAIM,
        from_id=claim_id,
        to_kind=EntityKind.ARTIFACT,
        to_id=artifact_id,
        relation="supports",
        weight=0.92,
    )
    explanation = ExplanationRecord(
        id=uuid4(),
        claim_id=claim_id,
        grade=EvidenceGrade.OBSERVED,
        method="tool_result_link",
        summary="Direct tool output supports the claim.",
        supporting_edge_ids=[edge_id],
        confidence=0.91,
    )

    assert session.status == SessionStatus.RUNNING
    assert trace.status == TraceStatus.RUNNING
    assert step.status == StepStatus.COMPLETED
    assert artifact.storage_ref == "s3://bucket/result.json"
    assert claim.verification_status == ClaimVerificationStatus.SUPPORTED
    assert edge.to_kind == EntityKind.ARTIFACT
    assert explanation.grade == EvidenceGrade.OBSERVED
    assert explanation.supporting_edge_ids == [edge_id]

