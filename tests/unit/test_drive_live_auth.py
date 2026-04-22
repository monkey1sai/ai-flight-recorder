from pathlib import Path

import httpx

from apps.api.app.connectors import FixtureDriveConnector, LiveDriveConnector
from apps.api.app.connectors.drive import (
    _drive_activity_from_api,
    build_drive_files_query,
    classify_drive_export_error,
)
from apps.api.app.settings import get_settings


def test_settings_parse_drive_oauth_paths(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AERIS_DRIVE_CONNECTOR_MODE", "live")
    monkeypatch.setenv("AERIS_GOOGLE_CLIENT_SECRETS_PATH", str(tmp_path / "credentials.json"))
    monkeypatch.setenv("AERIS_GOOGLE_TOKEN_PATH", str(tmp_path / "token.json"))
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.drive_connector_mode == "live"
    assert settings.google_client_secrets_path == tmp_path / "credentials.json"
    assert settings.google_token_path == tmp_path / "token.json"

    get_settings.cache_clear()


def test_fixture_drive_auth_status_is_explicit() -> None:
    status = FixtureDriveConnector().auth_status()

    assert status.mode == "fixture"
    assert status.connector_kind == "fixture"
    assert status.authorized is False
    assert status.blocked_reason == "fixture_mode"


def test_live_drive_auth_status_blocks_when_client_secrets_missing(tmp_path: Path) -> None:
    settings = get_settings().model_copy(
        update={
            "drive_connector_mode": "live",
            "google_client_secrets_path": tmp_path / "credentials.json",
            "google_token_path": tmp_path / "token.json",
        }
    )

    status = LiveDriveConnector(settings).auth_status()

    assert status.mode == "live"
    assert status.client_secrets_configured is True
    assert status.client_secrets_exists is False
    assert status.authorized is False
    assert status.blocked_reason == "client_secrets_file_not_found"


def test_live_drive_auth_status_requires_token_when_client_secrets_exist(tmp_path: Path) -> None:
    client_secrets = tmp_path / "credentials.json"
    client_secrets.write_text("{}", encoding="utf-8")
    settings = get_settings().model_copy(
        update={
            "drive_connector_mode": "live",
            "google_client_secrets_path": client_secrets,
            "google_token_path": tmp_path / "token.json",
        }
    )

    status = LiveDriveConnector(settings).auth_status()

    assert status.client_secrets_exists is True
    assert status.token_present is False
    assert status.authorized is False
    assert status.blocked_reason == "missing_token"


def test_build_drive_files_query_uses_full_text_contains() -> None:
    query = build_drive_files_query("incident notes")

    assert "trashed = false" in query
    assert "fullText contains 'incident'" in query
    assert "fullText contains 'notes'" in query


def test_classify_drive_export_error_maps_too_large() -> None:
    request = httpx.Request("GET", "https://www.googleapis.com/drive/v3/files/123/export")
    response = httpx.Response(
        403,
        request=request,
        text=(
            '{"error":{"message":"This file is too large to be exported",'
            '"status":"FAILED_PRECONDITION",'
            '"details":["exportSizeLimitExceeded 10 MB"]}}'
        ),
    )
    error = httpx.HTTPStatusError("export failed", request=request, response=response)

    assert classify_drive_export_error(error) == "export_too_large"


def test_drive_activity_parser_extracts_core_fields() -> None:
    activity = {
        "timestamp": {"time": "2026-04-22T02:30:00Z"},
        "primaryActionDetail": {"edit": {}},
        "actors": [{"user": {"knownUser": {"personName": "people/123"}}}],
        "targets": [{"driveItem": {"title": "Incident Notes", "name": "items/abc123"}}],
    }
    record = _drive_activity_from_api(
        "abc123",
        activity,
        "file:///tmp/activity.json",
    )

    assert record.source_id == "abc123"
    assert record.primary_action == "edit"
    assert record.actors == ["people/123"]
    assert record.targets == ["Incident Notes"]
    assert record.raw_ref == "file:///tmp/activity.json"
    assert len(record.id.split(":")[-1]) == 24
