from __future__ import annotations

from functools import lru_cache

from apps.api.app.connectors import FixtureArxivConnector, FixtureDriveConnector
from apps.api.app.repositories import FixtureTraceRepository
from apps.api.app.services import (
    GovernanceService,
    ReplayService,
    ResearchService,
    TraceWorkbenchService,
)


@lru_cache
def get_repository() -> FixtureTraceRepository:
    return FixtureTraceRepository.seeded()


@lru_cache
def get_trace_workbench_service() -> TraceWorkbenchService:
    return TraceWorkbenchService(get_repository())


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
