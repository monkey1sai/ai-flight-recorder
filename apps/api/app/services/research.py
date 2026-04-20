from __future__ import annotations

from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector
from apps.api.app.repositories import FixtureTraceRepository
from packages.schema.flight_recorder_schema import ResearchSearchResponse


class ResearchService:
    def __init__(
        self,
        repository: FixtureTraceRepository,
        drive_connector: FixtureDriveConnector,
        arxiv_connector: FixtureArxivConnector,
    ) -> None:
        self.repository = repository
        self.drive_connector = drive_connector
        self.arxiv_connector = arxiv_connector

    def search_drive(self, query: str) -> ResearchSearchResponse:
        response = self.drive_connector.search(query)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_search",
            actor="api",
            outcome="served",
            metadata_json={"query": query, "matches": len(response.items)},
        )
        return response

    def search_arxiv(self, query: str) -> ResearchSearchResponse:
        response = self.arxiv_connector.search(query)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.arxiv_search",
            actor="api",
            outcome="served",
            metadata_json={"query": query, "matches": len(response.items)},
        )
        return response
