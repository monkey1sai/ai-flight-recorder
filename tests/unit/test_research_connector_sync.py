from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector


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
