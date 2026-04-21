from __future__ import annotations

from functools import lru_cache

from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector
from apps.api.app.repositories import (
    FixtureTraceRepository,
    PostgresTraceRepository,
    TraceRepository,
)
from apps.api.app.services import (
    GovernanceService,
    ReplayService,
    ResearchService,
    TraceWorkbenchService,
)
from apps.api.app.settings import get_settings
from apps.api.app.storage import LocalBlobStore


@lru_cache
def get_repository() -> TraceRepository:
    settings = get_settings()
    if settings.repository_backend in {"postgres", "auto"}:
        try:
            repository = PostgresTraceRepository(settings.database_url)
            repository.ping()
            return repository
        except Exception:
            if settings.repository_backend == "postgres":
                raise
    return FixtureTraceRepository.seeded()


@lru_cache
def get_blob_store() -> LocalBlobStore:
    return LocalBlobStore(get_settings().blob_storage_root)


@lru_cache
def get_trace_workbench_service() -> TraceWorkbenchService:
    return TraceWorkbenchService(get_repository(), get_blob_store())


@lru_cache
def get_replay_service() -> ReplayService:
    return ReplayService(get_repository())


@lru_cache
def get_governance_service() -> GovernanceService:
    return GovernanceService(get_repository())


@lru_cache
def get_research_service() -> ResearchService:
    return ResearchService(
        repository=get_repository(),
        drive_connector=FixtureDriveConnector(),
        arxiv_connector=FixtureArxivConnector(),
    )
