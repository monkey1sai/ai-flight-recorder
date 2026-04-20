from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from apps.api.app.dependencies import get_governance_service
from apps.api.app.services import GovernanceService
from packages.schema.flight_recorder_schema import GovernanceSnapshotView

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/snapshot", response_model=GovernanceSnapshotView)
def get_governance_snapshot(
    trace_id: UUID | None = Query(default=None),
    service: GovernanceService = Depends(get_governance_service),
) -> GovernanceSnapshotView:
    return service.get_snapshot(trace_id)
