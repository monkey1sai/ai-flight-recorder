from __future__ import annotations

from apps.api.app.dependencies import get_research_service
from packages.schema.flight_recorder_schema import ResearchSyncReceipt


def sync_drive_query(query: str) -> ResearchSyncReceipt:
    return get_research_service().sync_drive(query)
