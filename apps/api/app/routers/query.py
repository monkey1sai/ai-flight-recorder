from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from apps.api.app.dependencies import get_trace_workbench_service
from apps.api.app.services import TraceWorkbenchService
from packages.schema.flight_recorder_schema import (
    ClaimEvidenceFlowView,
    StateDiffEntryView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)

router = APIRouter(prefix="/api/v1/traces", tags=["query"])


@router.get("", response_model=list[TraceSummaryView])
def list_traces(
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> list[TraceSummaryView]:
    return service.list_traces()


@router.get("/{trace_id}", response_model=TraceBundleView)
def get_trace(
    trace_id: UUID,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> TraceBundleView:
    bundle = service.get_trace_bundle(trace_id)
    if bundle is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return bundle


@router.get("/{trace_id}/timeline", response_model=list[TimelineEntryView])
def get_timeline(
    trace_id: UUID,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> list[TimelineEntryView]:
    timeline = service.get_timeline(trace_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="trace not found")
    return timeline


@router.get("/{trace_id}/state-diff", response_model=list[StateDiffEntryView])
def get_state_diff(
    trace_id: UUID,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> list[StateDiffEntryView]:
    state_diff = service.get_state_diffs(trace_id)
    if not state_diff:
        raise HTTPException(status_code=404, detail="trace not found")
    return state_diff


@router.get("/{trace_id}/claim-evidence", response_model=list[ClaimEvidenceFlowView])
def get_claim_evidence(
    trace_id: UUID,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> list[ClaimEvidenceFlowView]:
    claim_flow = service.get_claim_flow(trace_id)
    if not claim_flow:
        raise HTTPException(status_code=404, detail="trace not found")
    return claim_flow
