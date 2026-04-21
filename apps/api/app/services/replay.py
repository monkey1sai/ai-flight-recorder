from __future__ import annotations

from uuid import UUID

from apps.api.app.repositories import TraceRepository
from packages.schema.flight_recorder_schema import ReplayFrameView


class ReplayService:
    def __init__(self, repository: TraceRepository) -> None:
        self.repository = repository

    def get_replay(self, trace_id: UUID) -> list[ReplayFrameView]:
        frames = self.repository.build_replay(trace_id)
        if frames:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="replay.generated",
                actor="api",
                outcome="served",
                metadata_json={"frames": len(frames)},
            )
        return frames
