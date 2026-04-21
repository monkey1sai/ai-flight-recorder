from __future__ import annotations

from apps.api.app.connectors import FixtureDriveConnector
from packages.schema.flight_recorder_schema import ResearchSearchResponse


def sync_drive_query(query: str) -> ResearchSearchResponse:
    connector = FixtureDriveConnector()
    return connector.search(query)
