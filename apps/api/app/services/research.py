from __future__ import annotations

from fastapi import HTTPException

from apps.api.app.connectors import DriveConnector, FixtureArxivConnector
from apps.api.app.repositories import TraceRepository
from packages.schema.flight_recorder_schema import (
    DriveActivityListView,
    DriveActivitySyncReceipt,
    DriveAuthStatusView,
    DriveChangeSyncReceipt,
    ResearchCorpusView,
    ResearchSearchResponse,
    ResearchSyncReceipt,
    ResearchSyncRunRecord,
)


class ResearchService:
    def __init__(
        self,
        repository: TraceRepository,
        drive_connector: DriveConnector,
        arxiv_connector: FixtureArxivConnector,
    ) -> None:
        self.repository = repository
        self.drive_connector = drive_connector
        self.arxiv_connector = arxiv_connector

    def search_drive(self, query: str) -> ResearchSearchResponse:
        self._ensure_drive_ready_for_live_calls()
        response = self.drive_connector.search(query)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_search",
            actor="api",
            outcome="served",
            metadata_json={"query": query, "matches": len(response.items)},
        )
        return response

    def drive_auth_status(self) -> DriveAuthStatusView:
        status = self.drive_connector.auth_status()
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_auth_status",
            actor="api",
            outcome="authorized" if status.authorized else (status.blocked_reason or "blocked"),
            metadata_json={
                "mode": status.mode,
                "connector_kind": status.connector_kind,
                "client_secrets_configured": status.client_secrets_configured,
                "client_secrets_exists": status.client_secrets_exists,
                "token_present": status.token_present,
            },
        )
        return status

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

    def sync_drive(self, query: str) -> ResearchSyncReceipt:
        self._ensure_drive_ready_for_live_calls()
        sync_result = self.drive_connector.sync(
            query,
            cursor=self._current_cursor("drive"),
        )
        receipt = self.repository.upsert_research_documents(
            source_type="drive",
            response=sync_result.response,
            cursor=sync_result.cursor,
            metadata_json=sync_result.metadata_json,
        )
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_sync",
            actor="worker",
            outcome="completed",
            metadata_json={
                "query": query,
                "cursor": sync_result.cursor,
                "items": receipt.item_count,
            },
        )
        return receipt

    def sync_arxiv(self, query: str) -> ResearchSyncReceipt:
        sync_result = self.arxiv_connector.sync(
            query,
            cursor=self._current_cursor("arxiv"),
        )
        receipt = self.repository.upsert_research_documents(
            source_type="arxiv",
            response=sync_result.response,
            cursor=sync_result.cursor,
            metadata_json=sync_result.metadata_json,
        )
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.arxiv_sync",
            actor="worker",
            outcome="completed",
            metadata_json={
                "query": query,
                "cursor": sync_result.cursor,
                "items": receipt.item_count,
            },
        )
        return receipt

    def sync_drive_changes(self) -> DriveChangeSyncReceipt:
        self._ensure_drive_ready_for_live_calls()
        current_cursor, cursor_metadata = self._resolve_drive_changes_cursor()
        result = self.drive_connector.sync_changes(
            cursor=current_cursor,
        )
        receipt_metadata = {
            **result.receipt.metadata_json,
            **result.metadata_json,
            **cursor_metadata,
        }
        receipt = result.receipt.model_copy(update={"metadata_json": receipt_metadata})
        if result.response.items:
            self.repository.upsert_research_documents(
                source_type="drive",
                response=result.response,
                cursor=receipt.cursor,
                metadata_json=receipt_metadata,
                persist_default_cursor=False,
            )
        if receipt.cursor is not None:
            self.repository.upsert_research_cursor(
                source_type="drive",
                cursor_key="changes_page_token",
                cursor_value=receipt.cursor,
                metadata_json={
                    **receipt_metadata,
                    "previous_cursor": receipt.previous_cursor,
                    "item_count": receipt.item_count,
                    "upserted_count": receipt.upserted_count,
                    "changed_source_ids": receipt.changed_source_ids,
                },
            )
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_changes_sync",
            actor="worker",
            outcome=receipt.blocked_reason or "completed",
            metadata_json={
                "previous_cursor": receipt.previous_cursor,
                "cursor": receipt.cursor,
                "items": receipt.item_count,
                "upserted": receipt.upserted_count,
                **receipt.metadata_json,
            },
        )
        return receipt

    def sync_drive_activity(self, source_id: str) -> DriveActivitySyncReceipt:
        self._ensure_drive_ready_for_live_calls()
        view = self.drive_connector.query_activity(source_id)
        stored_count = self.repository.upsert_drive_activity_events(source_id, view.items)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_activity_sync",
            actor="worker",
            outcome=view.blocked_reason or "completed",
            metadata_json={
                "source_id": source_id,
                "items": len(view.items),
                "stored": stored_count,
                "blocked_reason": view.blocked_reason,
                **view.metadata_json,
            },
        )
        return DriveActivitySyncReceipt(
            source_id=source_id,
            item_count=len(view.items),
            stored_count=stored_count,
            blocked_reason=view.blocked_reason,
            metadata_json=view.metadata_json,
        )

    def list_drive_activity(self, source_id: str) -> DriveActivityListView:
        view = self.repository.list_drive_activity_events(source_id)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.drive_activity_query",
            actor="api",
            outcome="served",
            metadata_json={"source_id": source_id, "items": len(view.items)},
        )
        return view

    def list_corpus(
        self,
        source_type: str | None = None,
        query: str = "",
    ) -> ResearchCorpusView:
        corpus = self.repository.list_research_documents(source_type=source_type, query=query)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.corpus_query",
            actor="api",
            outcome="served",
            metadata_json={
                "query": query,
                "source_type": source_type,
                "matches": len(corpus.items),
            },
        )
        return corpus

    def list_sync_runs(
        self,
        source_type: str | None = None,
    ) -> list[ResearchSyncRunRecord]:
        runs = self.repository.list_research_sync_runs(source_type=source_type)
        self.repository.record_audit_event(
            trace_id=None,
            event_type="research.sync_runs_query",
            actor="api",
            outcome="served",
            metadata_json={"source_type": source_type, "runs": len(runs)},
        )
        return runs

    def _current_cursor(self, source_type: str, cursor_key: str = "default") -> str | None:
        current = self.repository.get_research_cursor(
            source_type=source_type,
            cursor_key=cursor_key,
        )
        return None if current is None else current.cursor_value

    def _resolve_drive_changes_cursor(self) -> tuple[str | None, dict[str, object]]:
        current = self.repository.get_research_cursor(
            source_type="drive",
            cursor_key="changes_page_token",
        )
        if current is None:
            return None, {}
        status = self.drive_connector.auth_status()
        if status.connector_kind != "live":
            return current.cursor_value, {}
        connector_mode = str(current.metadata_json.get("connector_mode", ""))
        if current.cursor_value.startswith("drive-fixture:") or connector_mode == "fixture":
            return (
                None,
                {
                    "ignored_cursor": current.cursor_value,
                    "ignored_reason": "fixture_cursor_in_live_mode",
                },
            )
        return current.cursor_value, {}

    def _ensure_drive_ready_for_live_calls(self) -> None:
        status = self.drive_connector.auth_status()
        if status.connector_kind == "live" and not status.authorized:
            raise HTTPException(
                status_code=503,
                detail={
                    "reason": status.blocked_reason or "drive_not_authorized",
                    "mode": status.mode,
                },
            )
