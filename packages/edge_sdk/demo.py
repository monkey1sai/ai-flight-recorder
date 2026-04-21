from __future__ import annotations

from apps.api.app.bootstrap import build_demo_ingest_request
from packages.schema.flight_recorder_schema import NormalizedTraceBundleIngestRequest


def build_demo_request() -> NormalizedTraceBundleIngestRequest:
    return build_demo_ingest_request(blob_seed_root="edge-sdk")
