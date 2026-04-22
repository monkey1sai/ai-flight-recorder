from datetime import UTC, datetime

from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector
from apps.api.app.repositories import FixtureTraceRepository
from apps.api.app.services import ResearchService
from packages.schema.flight_recorder_schema import (
    DriveActivityListView,
    DriveAuthStatusView,
    DriveChangeSyncReceipt,
    DriveChangeSyncResult,
    ResearchConnectorSyncResult,
    ResearchSearchResponse,
)


def test_drive_sync_result_preserves_cursor_and_export_status() -> None:
    result = FixtureDriveConnector().sync("incident notes")

    assert result.source_type == "drive"
    assert result.cursor is not None
    assert result.cursor.startswith("drive-fixture:")
    assert result.response.items[0].provenance.cursor == result.cursor
    assert result.response.items[0].provenance.export_status == "exported"


def test_arxiv_sync_result_preserves_cursor_and_export_status() -> None:
    result = FixtureArxivConnector().sync("faithful explanations provenance")

    assert result.source_type == "arxiv"
    assert result.cursor is not None
    assert result.cursor.startswith("oai-fixture:")
    assert result.response.items[0].provenance.cursor == result.cursor
    assert result.response.items[0].provenance.export_status == "metadata_only"


class _RecordingLiveDriveConnector:
    def __init__(self) -> None:
        self.received_cursor: str | None = None

    def auth_status(self) -> DriveAuthStatusView:
        return DriveAuthStatusView(
            mode="live",
            connector_kind="live",
            authorized=True,
            client_secrets_configured=True,
            client_secrets_exists=True,
            token_present=True,
        )

    def search(self, query: str) -> ResearchSearchResponse:
        return ResearchSearchResponse(query=query, items=[])

    def sync(
        self,
        query: str,
        cursor: str | None = None,
    ) -> ResearchConnectorSyncResult:
        raise AssertionError("sync should not be called in this test")

    def sync_changes(self, cursor: str | None = None) -> DriveChangeSyncResult:
        self.received_cursor = cursor
        return DriveChangeSyncResult(
            response=ResearchSearchResponse(query="", items=[]),
            receipt=DriveChangeSyncReceipt(
                previous_cursor=cursor,
                cursor="165387",
                item_count=0,
                upserted_count=0,
                changed_source_ids=[],
                metadata_json={"connector_mode": "live"},
            ),
            metadata_json={"connector_mode": "live"},
        )

    def query_activity(self, source_id: str) -> DriveActivityListView:
        return DriveActivityListView(source_id=source_id, items=[])

    def authorize_interactive(self) -> DriveAuthStatusView:
        return self.auth_status()


def test_live_change_sync_ignores_fixture_cursor_residue() -> None:
    repository = FixtureTraceRepository.seeded()
    repository.upsert_research_cursor(
        source_type="drive",
        cursor_key="changes_page_token",
        cursor_value="drive-fixture:changes:incident-notes",
        metadata_json={"connector_mode": "fixture", "updated_at": datetime.now(UTC).isoformat()},
    )
    connector = _RecordingLiveDriveConnector()
    service = ResearchService(
        repository=repository,
        drive_connector=connector,
        arxiv_connector=FixtureArxivConnector(),
    )

    receipt = service.sync_drive_changes()

    assert connector.received_cursor is None
    assert receipt.cursor == "165387"
    assert receipt.metadata_json["ignored_reason"] == "fixture_cursor_in_live_mode"
    assert receipt.metadata_json["ignored_cursor"] == "drive-fixture:changes:incident-notes"
