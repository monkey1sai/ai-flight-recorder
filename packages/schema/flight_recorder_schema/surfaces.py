from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .canonical import (
    ArtifactRecord,
    ClaimRecord,
    ClaimVerificationStatus,
    EvaluationRecord,
    EvidenceEdgeRecord,
    EvidenceGrade,
    ExplanationRecord,
    InterventionRecord,
    ObservationRecord,
    PlanVersionRecord,
    SessionRecord,
    StateDeltaRecord,
    StateSnapshotRecord,
    StepRecord,
    StepStatus,
    TaskRecord,
    TraceRecord,
    TraceStatus,
)


class AuditEventRecord(BaseModel):
    id: UUID
    trace_id: UUID | None = None
    event_type: str
    actor: str
    outcome: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class PolicyRuleRecord(BaseModel):
    id: UUID
    name: str
    category: str
    mode: str
    applies_to: list[str] = Field(default_factory=list)
    description: str
    configured_by: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class RetentionPolicyRecord(BaseModel):
    id: UUID
    name: str
    applies_to: list[str] = Field(default_factory=list)
    retention_days: int = Field(ge=1)
    purge_strategy: str
    redaction_scope: list[str] = Field(default_factory=list)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class TraceBundleView(BaseModel):
    session: SessionRecord
    trace: TraceRecord
    tasks: list[TaskRecord] = Field(default_factory=list)
    plan_versions: list[PlanVersionRecord] = Field(default_factory=list)
    state_snapshots: list[StateSnapshotRecord] = Field(default_factory=list)
    steps: list[StepRecord] = Field(default_factory=list)
    observations: list[ObservationRecord] = Field(default_factory=list)
    state_deltas: list[StateDeltaRecord] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    evidence_edges: list[EvidenceEdgeRecord] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    explanations: list[ExplanationRecord] = Field(default_factory=list)
    evaluations: list[EvaluationRecord] = Field(default_factory=list)
    interventions: list[InterventionRecord] = Field(default_factory=list)
    audit_events: list[AuditEventRecord] = Field(default_factory=list)
    policies: list[PolicyRuleRecord] = Field(default_factory=list)
    retention: list[RetentionPolicyRecord] = Field(default_factory=list)


class IngestReceipt(BaseModel):
    session_id: UUID
    trace_id: UUID
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    entity_counts: dict[str, int]
    audit_event_id: UUID | None = None


class RawArtifactPayload(BaseModel):
    artifact_id: UUID
    namespace: str = "artifacts"
    mime_type: str | None = None
    text_content: str | None = None
    json_content: dict[str, Any] | list[Any] | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class NormalizedTraceBundleIngestRequest(BaseModel):
    bundle: TraceBundleView
    raw_artifacts: list[RawArtifactPayload] = Field(default_factory=list)


class TraceSummaryView(BaseModel):
    trace_id: UUID
    session_id: UUID
    status: TraceStatus
    model_name: str | None = None
    trace_kind: str
    started_at: datetime
    ended_at: datetime | None = None
    step_count: int = 0
    claim_count: int = 0
    unsupported_claim_count: int = 0
    latest_audit_outcome: str | None = None


class TaskStateView(BaseModel):
    task: TaskRecord
    latest_plan: PlanVersionRecord | None = None
    latest_snapshot: StateSnapshotRecord | None = None
    plan_revision_count: int = 0
    snapshot_count: int = 0


class TimelineEntryView(BaseModel):
    step_id: UUID
    step_index: int = Field(ge=0)
    step_type: str
    actor: str
    status: StepStatus
    summary: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    evidence_grade: EvidenceGrade
    observation_count: int = 0
    artifact_ids: list[UUID] = Field(default_factory=list)
    claim_ids: list[UUID] = Field(default_factory=list)
    intervention_ids: list[UUID] = Field(default_factory=list)


class StateDiffEntryView(BaseModel):
    step_id: UUID
    step_index: int = Field(ge=0)
    facet: str
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ClaimEvidenceFlowView(BaseModel):
    claim: ClaimRecord
    verification_status: ClaimVerificationStatus
    explanations: list[ExplanationRecord] = Field(default_factory=list)
    supporting_edges: list[EvidenceEdgeRecord] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    supporting_step_ids: list[UUID] = Field(default_factory=list)


class ReplayFrameView(BaseModel):
    frame_index: int = Field(ge=0)
    step: StepRecord
    observations: list[ObservationRecord] = Field(default_factory=list)
    state_deltas: list[StateDeltaRecord] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    interventions: list[InterventionRecord] = Field(default_factory=list)


class ResearchSourceRecord(BaseModel):
    source_type: str
    source_id: str
    source_uri: str
    retrieved_at: datetime
    query: str
    license_or_terms_note: str | None = None
    checksum: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ResearchDocumentRecord(BaseModel):
    id: str
    title: str
    summary: str
    authors: list[str] = Field(default_factory=list)
    published_at: datetime | None = None
    mime_type: str | None = None
    content_ref: str | None = None
    tags: list[str] = Field(default_factory=list)
    provenance: ResearchSourceRecord


class ResearchSearchResponse(BaseModel):
    query: str
    items: list[ResearchDocumentRecord] = Field(default_factory=list)


class GovernanceSnapshotView(BaseModel):
    audit_events: list[AuditEventRecord] = Field(default_factory=list)
    policies: list[PolicyRuleRecord] = Field(default_factory=list)
    retention: list[RetentionPolicyRecord] = Field(default_factory=list)
