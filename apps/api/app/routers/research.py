from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from apps.api.app.dependencies import get_research_service
from apps.api.app.services import ResearchService
from packages.schema.flight_recorder_schema import (
    ResearchCorpusView,
    ResearchSearchResponse,
    ResearchSyncReceipt,
    ResearchSyncRunRecord,
)

router = APIRouter(prefix="/api/v1/research", tags=["research"])


@router.get("/drive/search", response_model=ResearchSearchResponse)
def search_drive(
    q: str = Query(default="", description="Drive search query."),
    service: ResearchService = Depends(get_research_service),
) -> ResearchSearchResponse:
    return service.search_drive(q)


@router.get("/arxiv/search", response_model=ResearchSearchResponse)
def search_arxiv(
    q: str = Query(default="", description="arXiv metadata query."),
    service: ResearchService = Depends(get_research_service),
) -> ResearchSearchResponse:
    return service.search_arxiv(q)


@router.post("/drive/sync", response_model=ResearchSyncReceipt)
def sync_drive(
    q: str = Query(default="", description="Drive sync query."),
    service: ResearchService = Depends(get_research_service),
) -> ResearchSyncReceipt:
    return service.sync_drive(q)


@router.post("/arxiv/sync", response_model=ResearchSyncReceipt)
def sync_arxiv(
    q: str = Query(default="", description="arXiv sync query."),
    service: ResearchService = Depends(get_research_service),
) -> ResearchSyncReceipt:
    return service.sync_arxiv(q)


@router.get("/corpus", response_model=ResearchCorpusView)
def list_corpus(
    q: str = Query(default="", description="Corpus search query."),
    source_type: str | None = Query(default=None, description="Optional source filter."),
    service: ResearchService = Depends(get_research_service),
) -> ResearchCorpusView:
    return service.list_corpus(source_type=source_type, query=q)


@router.get("/sync-runs", response_model=list[ResearchSyncRunRecord])
def list_sync_runs(
    source_type: str | None = Query(default=None, description="Optional source filter."),
    service: ResearchService = Depends(get_research_service),
) -> list[ResearchSyncRunRecord]:
    return service.list_sync_runs(source_type=source_type)
