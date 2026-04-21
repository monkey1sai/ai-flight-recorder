from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SessionStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TraceStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class TaskStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EvidenceGrade(StrEnum):
    OBSERVED = "observed"
    SELF_REPORTED = "self_reported"
    INFERRED = "inferred"
    VERIFIED = "verified"


class ClaimVerificationStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    MODEL_PRIOR_ONLY = "model_prior_only"
    CONFLICTED = "conflicted"


class EntityKind(StrEnum):
    TRACE = "trace"
    STEP = "step"
    OBSERVATION = "observation"
    STATE_DELTA = "state_delta"
    ARTIFACT = "artifact"
    CLAIM = "claim"
    EXPLANATION_RECORD = "explanation_record"
    EVALUATION = "evaluation"
    INTERVENTION = "intervention"


class FlightRecorderBase(BaseModel):
    id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SessionRecord(FlightRecorderBase):
    source: str
    user_id: str | None = None
    project_id: UUID | None = None
    external_conversation_id: str | None = None
    started_at: datetime
    ended_at: datetime | None = None
    status: SessionStatus = SessionStatus.QUEUED
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    labels_jsonb: list[str] = Field(default_factory=list)


class TraceRecord(FlightRecorderBase):
    session_id: UUID
    parent_trace_id: UUID | None = None
    task_id: UUID | None = None
    model_name: str | None = None
    trace_kind: str = "agent_run"
    started_at: datetime
    ended_at: datetime | None = None
    status: TraceStatus = TraceStatus.QUEUED
    config_ref: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class TaskRecord(FlightRecorderBase):
    session_id: UUID
    trace_id: UUID
    title: str
    status: TaskStatus = TaskStatus.QUEUED
    owner: str | None = None
    summary: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class StepRecord(FlightRecorderBase):
    trace_id: UUID
    parent_step_id: UUID | None = None
    step_index: int = Field(ge=0)
    step_type: str
    actor: str
    started_at: datetime
    ended_at: datetime | None = None
    status: StepStatus = StepStatus.QUEUED
    summary: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ArtifactRecord(FlightRecorderBase):
    source_type: str
    source_system: str | None = None
    source_uri: str | None = None
    mime_type: str | None = None
    checksum: str | None = None
    storage_ref: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ObservationRecord(FlightRecorderBase):
    step_id: UUID
    kind: str
    content_ref: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    source_artifact_id: UUID | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class StateDeltaRecord(FlightRecorderBase):
    step_id: UUID
    facet: str
    before_json: dict[str, Any] | None = None
    after_json: dict[str, Any] | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class PlanVersionRecord(FlightRecorderBase):
    task_id: UUID
    trace_id: UUID
    step_id: UUID | None = None
    revision: int = Field(ge=0)
    summary: str | None = None
    plan_json: dict[str, Any] = Field(default_factory=dict)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class StateSnapshotRecord(FlightRecorderBase):
    trace_id: UUID
    step_id: UUID | None = None
    task_id: UUID | None = None
    snapshot_index: int = Field(ge=0)
    state_json: dict[str, Any] = Field(default_factory=dict)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ClaimRecord(FlightRecorderBase):
    trace_id: UUID
    claim_text: str
    claim_type: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    position_index: int = Field(ge=0)
    verification_status: ClaimVerificationStatus = ClaimVerificationStatus.UNSUPPORTED
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class EvidenceEdgeRecord(FlightRecorderBase):
    from_kind: EntityKind
    from_id: UUID
    to_kind: EntityKind
    to_id: UUID
    relation: str
    weight: float | None = Field(default=None, ge=0, le=1)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class ExplanationRecord(FlightRecorderBase):
    claim_id: UUID
    grade: EvidenceGrade
    method: str
    summary: str
    supporting_edge_ids: list[UUID] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class EvaluationRecord(FlightRecorderBase):
    trace_id: UUID
    suite_name: str
    metric_name: str
    score: float | None = None
    verdict: str
    details_json: dict[str, Any] = Field(default_factory=dict)


class InterventionRecord(FlightRecorderBase):
    trace_id: UUID
    step_id: UUID | None = None
    intervention_type: str
    reason: str
    actor: str
    result: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)
