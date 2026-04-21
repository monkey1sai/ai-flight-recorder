from __future__ import annotations

import httpx

from packages.schema.flight_recorder_schema import (
    IngestReceipt,
    NormalizedTraceBundleIngestRequest,
)


class AerisEdgeClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def ingest(self, request: NormalizedTraceBundleIngestRequest) -> IngestReceipt:
        response = httpx.post(
            f"{self.base_url}/api/v1/ingest/normalized-trace-bundles",
            json=request.model_dump(mode="json"),
            timeout=30,
        )
        response.raise_for_status()
        return IngestReceipt.model_validate(response.json())
