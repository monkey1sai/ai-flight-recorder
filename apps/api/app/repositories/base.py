from __future__ import annotations

from typing import Protocol
from uuid import UUID

from packages.schema.flight_recorder_schema import (
    AuditEventRecord,
    ClaimEvidenceFlowView,
    IngestReceipt,
    PlanVersionRecord,
    ReplayFrameView,
    RetentionPolicyRecord,
    StateDiffEntryView,
    StateSnapshotRecord,
    TaskStateView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)


class TraceRepository(Protocol):
    def list_traces(self) -> list[TraceSummaryView]: ...

    def get_trace_bundle(self, trace_id: UUID) -> TraceBundleView | None: ...

    def upsert_bundle(self, bundle: TraceBundleView) -> IngestReceipt: ...

    def build_timeline(self, trace_id: UUID) -> list[TimelineEntryView]: ...

    def build_state_diffs(self, trace_id: UUID) -> list[StateDiffEntryView]: ...

    def build_claim_flows(self, trace_id: UUID) -> list[ClaimEvidenceFlowView]: ...

    def build_replay(self, trace_id: UUID) -> list[ReplayFrameView]: ...

    def get_task_state(self, trace_id: UUID) -> TaskStateView | None: ...

    def list_plan_versions(self, trace_id: UUID) -> list[PlanVersionRecord]: ...

    def list_state_snapshots(self, trace_id: UUID) -> list[StateSnapshotRecord]: ...

    def list_audit_events(self, trace_id: UUID | None = None) -> list[AuditEventRecord]: ...

    def list_policies(self) -> list: ...

    def list_retention(self) -> list[RetentionPolicyRecord]: ...

    def record_audit_event(
        self,
        trace_id: UUID | None,
        event_type: str,
        actor: str,
        outcome: str,
        metadata_json: dict[str, object] | None = None,
    ) -> AuditEventRecord: ...
