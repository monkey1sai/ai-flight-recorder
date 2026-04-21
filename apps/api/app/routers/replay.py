from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from apps.api.app.dependencies import get_replay_service
from apps.api.app.services import ReplayService
from packages.schema.flight_recorder_schema import ReplayFrameView, ReplayVerificationView

router = APIRouter(prefix="/api/v1/replay", tags=["replay"])


@router.get("/{trace_id}", response_model=list[ReplayFrameView])
def get_replay(
    trace_id: UUID,
    service: ReplayService = Depends(get_replay_service),
) -> list[ReplayFrameView]:
    frames = service.get_replay(trace_id)
    if not frames:
        raise HTTPException(status_code=404, detail="trace not found")
    return frames


@router.get("/{trace_id}/verification", response_model=ReplayVerificationView)
def get_replay_verification(
    trace_id: UUID,
    service: ReplayService = Depends(get_replay_service),
) -> ReplayVerificationView:
    verification = service.get_replay_verification(trace_id)
    if verification is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return verification


@router.post("/{trace_id}/verify", response_model=ReplayVerificationView)
def verify_trace(
    trace_id: UUID,
    service: ReplayService = Depends(get_replay_service),
) -> ReplayVerificationView:
    verification = service.verify_trace(trace_id)
    if verification is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return verification
