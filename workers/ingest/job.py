from __future__ import annotations

from apps.api.app.repositories import FixtureTraceRepository
from apps.api.app.services import TraceWorkbenchService
from packages.schema.flight_recorder_schema import IngestReceipt, TraceBundleView
from packages.testkit import load_trace_bundle_fixture


def seed_ingest_bundle(bundle: TraceBundleView | None = None) -> IngestReceipt:
    repository = FixtureTraceRepository.seeded()
    service = TraceWorkbenchService(repository)
    return service.ingest(bundle or load_trace_bundle_fixture())
