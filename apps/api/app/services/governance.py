from __future__ import annotations

from uuid import UUID

from apps.api.app.repositories import FixtureTraceRepository
from packages.schema.flight_recorder_schema import GovernanceSnapshotView


class GovernanceService:
    def __init__(self, repository: FixtureTraceRepository) -> None:
        self.repository = repository

    def get_snapshot(self, trace_id: UUID | None = None) -> GovernanceSnapshotView:
        snapshot = GovernanceSnapshotView(
            audit_events=self.repository.list_audit_events(trace_id),
            policies=self.repository.list_policies(),
            retention=self.repository.list_retention(),
        )
        self.repository.record_audit_event(
            trace_id=trace_id,
            event_type="admin.snapshot",
            actor="api",
            outcome="served",
            metadata_json={"trace_scoped": trace_id is not None},
        )
        return snapshot
