from __future__ import annotations

from functools import lru_cache

from apps.api.app.connectors import (
    FixtureArxivConnector,
    FixtureDriveConnector,
    LiveDriveConnector,
)
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
    settings = get_settings()
    drive_connector = FixtureDriveConnector()
    if settings.drive_connector_mode == "live":
        drive_connector = LiveDriveConnector(settings, get_blob_store())
    elif (
        settings.drive_connector_mode == "auto"
        and settings.google_client_secrets_path is not None
    ):
        drive_connector = LiveDriveConnector(settings, get_blob_store())

    return ResearchService(
        repository=get_repository(),
        drive_connector=drive_connector,
        arxiv_connector=FixtureArxivConnector(),
    )
