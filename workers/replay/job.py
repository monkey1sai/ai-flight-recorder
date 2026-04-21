from __future__ import annotations

from uuid import UUID

from apps.api.app.repositories import FixtureTraceRepository
from apps.api.app.services import ReplayService
from packages.schema.flight_recorder_schema import ReplayFrameView, ReplayVerificationView


def generate_replay_frames(trace_id: UUID) -> list[ReplayFrameView]:
    repository = FixtureTraceRepository.seeded()
    service = ReplayService(repository)
    return service.get_replay(trace_id)


def generate_replay_verification(trace_id: UUID) -> ReplayVerificationView | None:
    repository = FixtureTraceRepository.seeded()
    service = ReplayService(repository)
    return service.verify_trace(trace_id)
