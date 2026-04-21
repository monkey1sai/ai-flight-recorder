from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.app.dependencies import get_trace_workbench_service
from apps.api.app.services import TraceWorkbenchService
from packages.schema.flight_recorder_schema import IngestReceipt, TraceBundleView

router = APIRouter(prefix="/api/v1/ingest", tags=["ingest"])


@router.post("/trace-bundles", response_model=IngestReceipt)
def ingest_trace_bundle(
    bundle: TraceBundleView,
    service: TraceWorkbenchService = Depends(get_trace_workbench_service),
) -> IngestReceipt:
    return service.ingest(bundle)
