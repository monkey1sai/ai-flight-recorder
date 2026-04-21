from __future__ import annotations

from uuid import UUID

from apps.api.app.repositories import TraceRepository
from packages.schema.flight_recorder_schema import ReplayFrameView, ReplayVerificationView


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

    def get_replay_verification(self, trace_id: UUID) -> ReplayVerificationView | None:
        view = self.repository.get_replay_verification(trace_id)
        if view is not None:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="replay.verification.served",
                actor="api",
                outcome=view.verification_badge,
                metadata_json={
                    "verified_claim_count": view.verified_claim_count,
                    "claim_count": view.claim_count,
                },
            )
        return view

    def verify_trace(self, trace_id: UUID) -> ReplayVerificationView | None:
        view = self.repository.refresh_replay_verification(trace_id)
        if view is not None:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="replay.verification.generated",
                actor="api",
                outcome=view.verification_badge,
                metadata_json={
                    "verified_claim_count": view.verified_claim_count,
                    "claim_count": view.claim_count,
                    "replay_trace_ids": [str(item) for item in view.replay_trace_ids],
                },
            )
        return view
