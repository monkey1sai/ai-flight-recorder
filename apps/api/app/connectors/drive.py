from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import httpx

from apps.api.app.settings import AppSettings
from apps.api.app.storage import LocalBlobStore
from packages.schema.flight_recorder_schema import (
    DriveActivityListView,
    DriveActivityRecord,
    DriveAuthStatusView,
    DriveChangeSyncReceipt,
    DriveChangeSyncResult,
    ResearchConnectorSyncResult,
    ResearchDocumentRecord,
    ResearchSearchResponse,
    ResearchSourceRecord,
)
from packages.testkit import load_drive_search_fixture

DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
DOCS_READONLY_SCOPE = "https://www.googleapis.com/auth/documents.readonly"
DRIVE_ACTIVITY_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.activity.readonly"
GOOGLE_DRIVE_SCOPES = [
    DRIVE_READONLY_SCOPE,
    DOCS_READONLY_SCOPE,
    DRIVE_ACTIVITY_READONLY_SCOPE,
]
GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DOCS_API_BASE = "https://docs.googleapis.com/v1"
DRIVE_SEARCH_FIELDS = (
    "files("
    "id,name,mimeType,description,modifiedTime,webViewLink,"
    "owners(displayName),md5Checksum,size,trashed"
    ")"
)
DRIVE_CHANGE_FIELDS = (
    "changes("
    "fileId,"
    "file("
    "id,name,mimeType,description,modifiedTime,webViewLink,"
    "owners(displayName),md5Checksum,size,trashed"
    "),"
    "removed,time"
    "),"
    "nextPageToken,newStartPageToken"
)


class DriveConnector(Protocol):
    def auth_status(self) -> DriveAuthStatusView: ...

    def search(self, query: str) -> ResearchSearchResponse: ...

    def sync(
        self,
        query: str,
        cursor: str | None = None,
    ) -> ResearchConnectorSyncResult: ...

    def sync_changes(self, cursor: str | None = None) -> DriveChangeSyncResult: ...

    def query_activity(self, source_id: str) -> DriveActivityListView: ...

    def authorize_interactive(self) -> DriveAuthStatusView: ...


class FixtureDriveConnector:
    def __init__(self) -> None:
        self.seed = load_drive_search_fixture()

    def auth_status(self) -> DriveAuthStatusView:
        return DriveAuthStatusView(
            mode="fixture",
            connector_kind="fixture",
            authorized=False,
            client_secrets_configured=False,
            client_secrets_exists=False,
            token_present=False,
            blocked_reason="fixture_mode",
        )

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

    def sync_changes(self, cursor: str | None = None) -> DriveChangeSyncResult:
        next_cursor = f"drive-fixture:changes:{cursor or 'initial'}"
        return DriveChangeSyncResult(
            response=ResearchSearchResponse(query="", items=[]),
            receipt=DriveChangeSyncReceipt(
                previous_cursor=cursor,
                cursor=next_cursor,
            ),
            metadata_json={"connector_mode": "fixture"},
        )

    def query_activity(self, source_id: str) -> DriveActivityListView:
        return DriveActivityListView(source_id=source_id, items=[])

    def authorize_interactive(self) -> DriveAuthStatusView:
        return self.auth_status()


class LiveDriveConnector:
    def __init__(self, settings: AppSettings, blob_store: LocalBlobStore | None = None) -> None:
        self.settings = settings
        self.blob_store = blob_store

    def auth_status(self) -> DriveAuthStatusView:
        client_secrets = self.settings.google_client_secrets_path
        token_path = self.settings.google_token_path
        client_configured = client_secrets is not None
        client_exists = bool(client_secrets and client_secrets.exists())
        token_present = token_path.exists()

        if not client_configured:
            return self._status(
                authorized=False,
                client_secrets_configured=False,
                client_secrets_exists=False,
                token_present=token_present,
                blocked_reason="missing_client_secrets_path",
            )
        if not client_exists:
            return self._status(
                authorized=False,
                client_secrets_configured=True,
                client_secrets_exists=False,
                token_present=token_present,
                blocked_reason="client_secrets_file_not_found",
            )
        if not token_present:
            return self._status(
                authorized=False,
                client_secrets_configured=True,
                client_secrets_exists=True,
                token_present=False,
                blocked_reason="missing_token",
            )

        try:
            credentials = self._load_credentials(token_path)
        except Exception:
            return self._status(
                authorized=False,
                client_secrets_configured=True,
                client_secrets_exists=True,
                token_present=True,
                blocked_reason="invalid_token",
            )

        authorized = bool(credentials.valid)
        can_refresh = bool(credentials.expired and credentials.refresh_token)
        blocked_reason = None if (authorized or can_refresh) else "token_not_valid"
        return self._status(
            authorized=authorized or can_refresh,
            client_secrets_configured=True,
            client_secrets_exists=True,
            token_present=True,
            can_refresh=can_refresh,
            granted_scopes=list(credentials.scopes or GOOGLE_DRIVE_SCOPES),
            blocked_reason=blocked_reason,
        )

    def authorize_interactive(self) -> DriveAuthStatusView:
        client_secrets = self.settings.google_client_secrets_path
        if client_secrets is None:
            raise RuntimeError("AERIS_GOOGLE_CLIENT_SECRETS_PATH is required")
        if not client_secrets.exists():
            raise RuntimeError(f"Client secrets file not found: {client_secrets}")

        from google_auth_oauthlib.flow import InstalledAppFlow

        token_path = self.settings.google_token_path
        token_path.parent.mkdir(parents=True, exist_ok=True)
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secrets),
            GOOGLE_DRIVE_SCOPES,
        )
        credentials = flow.run_local_server(port=0)
        token_path.write_text(credentials.to_json(), encoding="utf-8")
        return self.auth_status()

    def search(self, query: str) -> ResearchSearchResponse:
        payload = self._request_json(
            "GET",
            f"{DRIVE_API_BASE}/files",
            params={
                "q": build_drive_files_query(query),
                "fields": DRIVE_SEARCH_FIELDS,
                "pageSize": "25",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            },
        )
        files = payload.get("files", [])
        return ResearchSearchResponse(
            query=query,
            items=[
                self._document_from_drive_file(item, query=query)
                for item in files
                if not item.get("trashed", False)
            ],
        )

    def sync(
        self,
        query: str,
        cursor: str | None = None,
    ) -> ResearchConnectorSyncResult:
        if self.blob_store is None:
            raise RuntimeError("blob_store is required for live drive sync")

        search_response = self.search(query)
        synced_items = [
            self._hydrate_document(item)
            for item in search_response.items
        ]
        next_cursor = f"drive-query:{query or 'all'}:{datetime.now(UTC).isoformat()}"
        enriched_response = ResearchSearchResponse(
            query=query,
            items=[
                item.model_copy(
                    update={
                        "provenance": item.provenance.model_copy(update={"cursor": next_cursor})
                    }
                )
                for item in synced_items
            ],
        )
        return ResearchConnectorSyncResult(
            source_type="drive",
            response=enriched_response,
            cursor=next_cursor,
            metadata_json={
                "connector_mode": "live",
                "cursor_in": cursor,
                "sync_kind": "search",
                "export_format": "text/plain",
            },
        )

    def sync_changes(self, cursor: str | None = None) -> DriveChangeSyncResult:
        endpoint = (
            f"{DRIVE_API_BASE}/changes/startPageToken"
            if cursor is None
            else f"{DRIVE_API_BASE}/changes"
        )
        payload = self._request_json(
            "GET",
            endpoint,
            params=None
            if cursor is None
            else {
                "pageToken": cursor,
                "fields": DRIVE_CHANGE_FIELDS,
                "pageSize": "50",
                "spaces": "drive",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            },
        )
        if cursor is None:
            next_cursor = str(payload["startPageToken"])
            return DriveChangeSyncResult(
                response=ResearchSearchResponse(query="", items=[]),
                receipt=DriveChangeSyncReceipt(
                    previous_cursor=None,
                    cursor=next_cursor,
                    item_count=0,
                    upserted_count=0,
                    changed_source_ids=[],
                ),
                metadata_json={"connector_mode": "live", "sync_kind": "changes"},
            )

        changed_files = [
            change["file"]
            for change in payload.get("changes", [])
            if isinstance(change, dict)
            and isinstance(change.get("file"), dict)
            and not change.get("removed", False)
            and not change["file"].get("trashed", False)
        ]
        changed_items = [
            self._hydrate_document(self._document_from_drive_file(file_record, query=""))
            if self.blob_store is not None and file_record.get("mimeType") == GOOGLE_DOC_MIME_TYPE
            else self._document_from_drive_file(file_record, query="")
            for file_record in changed_files
        ]
        next_cursor = payload.get("newStartPageToken") or payload.get("nextPageToken") or cursor
        return DriveChangeSyncResult(
            response=ResearchSearchResponse(query="", items=changed_items),
            receipt=DriveChangeSyncReceipt(
                previous_cursor=cursor,
                cursor=next_cursor,
                item_count=len(payload.get("changes", [])),
                upserted_count=len(changed_items),
                changed_source_ids=[item.provenance.source_id for item in changed_items],
            ),
            metadata_json={"connector_mode": "live", "sync_kind": "changes"},
        )

    def query_activity(self, source_id: str) -> DriveActivityListView:
        if self.blob_store is None:
            raise RuntimeError("blob_store is required for drive activity queries")
        payload = self._request_json(
            "POST",
            "https://driveactivity.googleapis.com/v2/activity:query",
            json_body={"itemName": f"items/{source_id}", "pageSize": 25},
        )
        events = []
        for activity in payload.get("activities", []):
            raw_blob = self.blob_store.put_json(
                "research/drive/activity",
                f"{source_id}-{len(events)}",
                activity,
            )
            events.append(_drive_activity_from_api(source_id, activity, raw_blob.storage_ref))
        return DriveActivityListView(source_id=source_id, items=events)

    def _status(
        self,
        *,
        authorized: bool,
        client_secrets_configured: bool,
        client_secrets_exists: bool,
        token_present: bool,
        can_refresh: bool = False,
        granted_scopes: list[str] | None = None,
        blocked_reason: str | None = None,
    ) -> DriveAuthStatusView:
        return DriveAuthStatusView(
            mode="live",
            connector_kind="live",
            authorized=authorized,
            client_secrets_configured=client_secrets_configured,
            client_secrets_exists=client_secrets_exists,
            token_present=token_present,
            can_refresh=can_refresh,
            granted_scopes=granted_scopes or [],
            blocked_reason=blocked_reason,
        )

    def _load_credentials(self, token_path: Path):
        from google.oauth2.credentials import Credentials

        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            GOOGLE_DRIVE_SCOPES,
        )
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request

            credentials.refresh(Request())
            token_path.write_text(credentials.to_json(), encoding="utf-8")
        return credentials

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        credentials = self._load_credentials(self.settings.google_token_path)
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method,
                url,
                params=params,
                json=json_body,
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
        response.raise_for_status()
        return response.json()

    def _request_bytes(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
    ) -> bytes:
        credentials = self._load_credentials(self.settings.google_token_path)
        with httpx.Client(timeout=60.0) as client:
            response = client.request(
                method,
                url,
                params=params,
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
        response.raise_for_status()
        return response.content

    def _document_from_drive_file(
        self,
        file_record: dict[str, Any],
        *,
        query: str,
    ) -> ResearchDocumentRecord:
        owners = file_record.get("owners", [])
        mime_type = file_record.get("mimeType")
        modified_time = file_record.get("modifiedTime")
        source_id = str(file_record["id"])
        source_uri = file_record.get("webViewLink") or f"https://drive.google.com/open?id={source_id}"
        tags = ["drive"]
        if mime_type == GOOGLE_DOC_MIME_TYPE:
            tags.append("google-doc")
        return ResearchDocumentRecord(
            id=f"drive:{source_id}",
            title=file_record.get("name") or source_id,
            summary=file_record.get("description") or "Google Drive document metadata.",
            authors=[
                owner.get("displayName", "unknown")
                for owner in owners
                if isinstance(owner, dict)
            ],
            published_at=_parse_google_datetime(modified_time),
            mime_type=mime_type,
            content_ref=None,
            tags=tags,
            provenance=ResearchSourceRecord(
                source_type="drive",
                source_id=source_id,
                source_uri=source_uri,
                retrieved_at=datetime.now(UTC),
                query=query,
                checksum=_normalize_drive_checksum(file_record.get("md5Checksum")),
                license_or_terms_note="Private workspace document; metadata and blob refs only.",
                metadata_json={
                    "connector_mode": "live",
                    "mimeType": mime_type,
                    "modifiedTime": modified_time,
                    "size": file_record.get("size"),
                },
            ),
        )

    def _hydrate_document(self, item: ResearchDocumentRecord) -> ResearchDocumentRecord:
        if self.blob_store is None:
            raise RuntimeError("blob_store is required for live drive sync")
        if item.mime_type != GOOGLE_DOC_MIME_TYPE:
            return item.model_copy(
                update={
                    "provenance": item.provenance.model_copy(
                        update={"export_status": "metadata_only"}
                    )
                }
            )

        docs_json = self._request_json(
            "GET",
            f"{DOCS_API_BASE}/documents/{item.provenance.source_id}",
        )
        docs_json_blob = self.blob_store.put_json(
            "research/drive/docs-json",
            item.provenance.source_id,
            docs_json,
        )
        metadata_json = dict(item.provenance.metadata_json)
        metadata_json["docs_json_ref"] = docs_json_blob.storage_ref

        export_status = "exported"
        content_ref = docs_json_blob.storage_ref
        checksum = docs_json_blob.checksum
        try:
            export_bytes = self._request_bytes(
                "GET",
                f"{DRIVE_API_BASE}/files/{item.provenance.source_id}/export",
                params={"mimeType": "text/plain"},
            )
            export_text = export_bytes.decode("utf-8", errors="ignore")
            export_blob = self.blob_store.put_text(
                "research/drive/exports",
                item.provenance.source_id,
                export_text,
                suffix=".txt",
            )
            content_ref = export_blob.storage_ref
            checksum = export_blob.checksum
        except httpx.HTTPStatusError as error:
            export_status = classify_drive_export_error(error)
            metadata_json["export_error"] = _summarize_http_error(error)

        return item.model_copy(
            update={
                "content_ref": content_ref,
                "provenance": item.provenance.model_copy(
                    update={
                        "checksum": checksum,
                        "export_status": export_status,
                        "metadata_json": metadata_json,
                    }
                ),
            }
        )


def build_drive_files_query(query: str) -> str:
    tokens = [token.strip() for token in query.split() if token.strip()]
    if not tokens:
        return "trashed = false"
    clauses = [f"fullText contains '{escape_drive_query_token(token)}'" for token in tokens]
    return "trashed = false and " + " and ".join(clauses)


def escape_drive_query_token(token: str) -> str:
    return token.replace("\\", "\\\\").replace("'", "\\'")


def classify_drive_export_error(error: httpx.HTTPStatusError) -> str:
    payload = error.response.text.lower()
    if "10 mb" in payload or "exportsizelimitexceeded" in payload:
        return "export_too_large"
    if error.response.status_code in {400, 403, 404}:
        return "export_unavailable"
    return "export_failed"


def _parse_google_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _normalize_drive_checksum(value: str | None) -> str | None:
    return None if not value else f"md5:{value}"


def _summarize_http_error(error: httpx.HTTPStatusError) -> dict[str, Any]:
    return {
        "status_code": error.response.status_code,
        "url": str(error.request.url),
    }


def _drive_activity_from_api(
    source_id: str,
    activity: dict[str, Any],
    raw_ref: str,
) -> DriveActivityRecord:
    actors = [_activity_actor_name(actor) for actor in activity.get("actors", [])]
    targets = [_activity_target_name(target) for target in activity.get("targets", [])]
    occurred_at = _activity_timestamp(activity)
    primary_action = _activity_primary_action(activity)
    event_id = f"{source_id}:{_activity_fingerprint(activity)}"
    return DriveActivityRecord(
        id=event_id,
        source_id=source_id,
        occurred_at=occurred_at,
        primary_action=primary_action,
        actors=[actor for actor in actors if actor],
        targets=[target for target in targets if target],
        raw_ref=raw_ref,
        metadata_json={"connector_mode": "live"},
    )


def _activity_fingerprint(activity: dict[str, Any]) -> str:
    payload = json.dumps(activity, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _activity_timestamp(activity: dict[str, Any]) -> datetime:
    time_range = activity.get("timestamp") or {}
    if isinstance(time_range, dict):
        if isinstance(time_range.get("time"), str):
            return _parse_google_datetime(time_range["time"]) or datetime.now(UTC)
        if isinstance(time_range.get("startTime"), str):
            return _parse_google_datetime(time_range["startTime"]) or datetime.now(UTC)
    return datetime.now(UTC)


def _activity_primary_action(activity: dict[str, Any]) -> str:
    actions = activity.get("primaryActionDetail") or {}
    if isinstance(actions, dict) and actions:
        return next(iter(actions.keys()))
    return "unknown"


def _activity_actor_name(actor: Any) -> str:
    if not isinstance(actor, dict):
        return ""
    user = actor.get("user")
    if isinstance(user, dict):
        known = user.get("knownUser")
        if isinstance(known, dict) and isinstance(known.get("personName"), str):
            return str(known["personName"])
    administrator = actor.get("administrator")
    if administrator:
        return "administrator"
    return "unknown"


def _activity_target_name(target: Any) -> str:
    if not isinstance(target, dict):
        return ""
    drive_item = target.get("driveItem")
    if isinstance(drive_item, dict):
        title = drive_item.get("title")
        name = drive_item.get("name")
        return str(title or name or "drive-item")
    return "target"
