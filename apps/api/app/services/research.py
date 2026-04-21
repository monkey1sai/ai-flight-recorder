from __future__ import annotations

from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector
from apps.api.app.repositories import TraceRepository
from packages.schema.flight_recorder_schema import (
    ResearchCorpusView,
    ResearchSearchResponse,
    ResearchSyncReceipt,
    ResearchSyncRunRecord,
)


class ResearchService:
    def __init__(
        self,
        repository: TraceRepository,
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

    def sync_drive(self, query: str) -> ResearchSyncReceipt:
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

    def _current_cursor(self, source_type: str) -> str | None:
        current = self.repository.get_research_cursor(source_type=source_type)
        return None if current is None else current.cursor_value
