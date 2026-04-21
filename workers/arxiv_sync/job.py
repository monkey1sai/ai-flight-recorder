from __future__ import annotations

from apps.api.app.connectors import FixtureArxivConnector
from packages.schema.flight_recorder_schema import ResearchSearchResponse


def sync_arxiv_query(query: str) -> ResearchSearchResponse:
    connector = FixtureArxivConnector()
    return connector.search(query)
