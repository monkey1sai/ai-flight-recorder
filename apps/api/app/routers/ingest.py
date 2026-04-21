from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_trace_workbench_service
from apps.api.app.services import TraceWorkbenchService
from packages.schema.flight_recorder_schema import (
    IngestReceipt,
    NormalizedTraceBundleIngestRequest,
    TraceBundleView,
)

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


@router.post("/trace-bundles", response_model=IngestReceipt)
def ingest_trace_bundle(
    bundle: TraceBundleView,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> IngestReceipt:
    return service.ingest(bundle)


@router.post("/normalized-trace-bundles", response_model=IngestReceipt)
def ingest_normalized_trace_bundle(
    request: NormalizedTraceBundleIngestRequest,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> IngestReceipt:
    return service.ingest_normalized(request)
