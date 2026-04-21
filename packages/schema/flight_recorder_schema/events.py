from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .canonical import EvidenceGrade


class StepEnvelope(BaseModel):
    session_id: UUID
    trace_id: UUID
    step_id: UUID
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    evidence_grade: EvidenceGrade
    summary: str = Field(min_length=1, max_length=2000)
    source_uri: str | None = None


class HealthStatus(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "api"
    evidence_grades: list[EvidenceGrade] = Field(default_factory=lambda: list(EvidenceGrade))
