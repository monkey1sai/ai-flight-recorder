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


class ReplayRunRecord(BaseModel):
    id: UUID
    trace_id: UUID
    status: str
    method: str
    frame_count: int = Field(ge=0)
    verified_claim_count: int = Field(ge=0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class VerificationRecord(BaseModel):
    id: UUID
    trace_id: UUID
    claim_id: UUID
    claim_text: str
    explanation_id: UUID | None = None
    replay_run_id: UUID | None = None
    verification_status: ClaimVerificationStatus
    evidence_grade: EvidenceGrade
    verification_badge: str
    method: str
    summary: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    replay_trace_id: UUID | None = None
    supporting_edge_ids: list[UUID] = Field(default_factory=list)
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReplayVerificationView(BaseModel):
    trace_id: UUID
    claim_count: int = Field(ge=0)
    verified_claim_count: int = Field(ge=0)
    verification_badge: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    replay_trace_ids: list[UUID] = Field(default_factory=list)
    replay_run: ReplayRunRecord | None = None
    verification_records: list[VerificationRecord] = Field(default_factory=list)


class ResearchSourceRecord(BaseModel):
    source_type: str
    source_id: str
    source_uri: str
    retrieved_at: datetime
    query: str
    cursor: str | None = None
    license_or_terms_note: str | None = None
    checksum: str | None = None
    export_status: str | None = None
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


class ResearchConnectorSyncResult(BaseModel):
    source_type: str
    response: ResearchSearchResponse
    cursor: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class DriveAuthStatusView(BaseModel):
    mode: str
    authorized: bool
    connector_kind: str
    client_secrets_configured: bool
    client_secrets_exists: bool
    token_present: bool
    can_refresh: bool = False
    granted_scopes: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None


class DriveChangeSyncReceipt(BaseModel):
    source_type: str = "drive"
    previous_cursor: str | None = None
    cursor: str | None = None
    item_count: int = 0
    upserted_count: int = 0
    changed_source_ids: list[str] = Field(default_factory=list)


class DriveChangeSyncResult(BaseModel):
    response: ResearchSearchResponse
    receipt: DriveChangeSyncReceipt
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class DriveActivityRecord(BaseModel):
    id: str
    source_id: str
    occurred_at: datetime
    primary_action: str
    actors: list[str] = Field(default_factory=list)
    targets: list[str] = Field(default_factory=list)
    raw_ref: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class DriveActivityListView(BaseModel):
    source_id: str
    items: list[DriveActivityRecord] = Field(default_factory=list)


class DriveActivitySyncReceipt(BaseModel):
    source_id: str
    item_count: int = 0
    stored_count: int = 0


class ResearchSyncRunRecord(BaseModel):
    id: UUID
    source_type: str
    query: str
    cursor: str | None = None
    status: str
    item_count: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ResearchSyncCursorRecord(BaseModel):
    source_type: str
    cursor_key: str
    cursor_value: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ResearchSyncReceipt(BaseModel):
    sync_run_id: UUID
    source_type: str
    query: str
    cursor: str | None = None
    item_count: int = 0
    upserted_count: int = 0


class ResearchCorpusView(BaseModel):
    query: str = ""
    source_type: str | None = None
    items: list[ResearchDocumentRecord] = Field(default_factory=list)


class GovernanceSnapshotView(BaseModel):
    audit_events: list[AuditEventRecord] = Field(default_factory=list)
    policies: list[PolicyRuleRecord] = Field(default_factory=list)
    retention: list[RetentionPolicyRecord] = Field(default_factory=list)
