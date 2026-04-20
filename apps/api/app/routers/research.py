from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from apps.api.app.dependencies import get_research_service
from apps.api.app.services import ResearchService
from packages.schema.flight_recorder_schema import ResearchSearchResponse

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
