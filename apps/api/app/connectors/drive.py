from __future__ import annotations

from packages.schema.flight_recorder_schema import (
    ResearchConnectorSyncResult,
    ResearchSearchResponse,
)
from packages.testkit import load_drive_search_fixture


class FixtureDriveConnector:
    def __init__(self) -> None:
        self.seed = load_drive_search_fixture()

    def search(self, query: str) -> ResearchSearchResponse:
        tokens = [token.strip().lower() for token in query.split() if token.strip()]

        if not tokens:
            return self.seed.model_copy(deep=True)

        matches = []
        for item in self.seed.items:
            haystack = " ".join([item.title, item.summary, *item.tags]).lower()
            if all(token in haystack for token in tokens):
                cloned = item.model_copy(deep=True)
                cloned.provenance.query = query
                matches.append(cloned)

        return ResearchSearchResponse(query=query, items=matches)

    def sync(
        self,
        query: str,
        cursor: str | None = None,
    ) -> ResearchConnectorSyncResult:
        response = self.search(query)
        next_cursor = f"drive-fixture:{query or 'all'}:{len(response.items)}"
        enriched_response = ResearchSearchResponse(
            query=response.query,
            items=[
                item.model_copy(
                    update={
                        "provenance": item.provenance.model_copy(
                            update={
                                "cursor": next_cursor,
                                "export_status": "exported",
                            }
                        )
                    }
                )
                for item in response.items
            ],
        )
        return ResearchConnectorSyncResult(
            source_type="drive",
            response=enriched_response,
            cursor=next_cursor,
            metadata_json={
                "connector_mode": "fixture",
                "cursor_in": cursor,
                "export_format": "google-docs-json",
            },
        )
