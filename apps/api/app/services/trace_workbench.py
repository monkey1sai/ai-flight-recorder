from __future__ import annotations

from uuid import UUID

from apps.api.app.repositories import FixtureTraceRepository
from packages.schema.flight_recorder_schema import (
    ClaimEvidenceFlowView,
    IngestReceipt,
    StateDiffEntryView,
    TimelineEntryView,
    TraceBundleView,
    TraceSummaryView,
)


class TraceWorkbenchService:
    def __init__(self, repository: FixtureTraceRepository) -> None:
        self.repository = repository

    def ingest(self, bundle: TraceBundleView) -> IngestReceipt:
        return self.repository.upsert_bundle(bundle)

    def list_traces(self) -> list[TraceSummaryView]:
        return self.repository.list_traces()

    def get_trace_bundle(self, trace_id: UUID) -> TraceBundleView | None:
        bundle = self.repository.get_trace_bundle(trace_id)
        if bundle is not None:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="query.trace_detail",
                actor="api",
                outcome="served",
                metadata_json={"surface": "trace_bundle"},
            )
        return bundle

    def get_timeline(self, trace_id: UUID) -> list[TimelineEntryView]:
        timeline = self.repository.build_timeline(trace_id)
        if timeline:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="query.timeline",
                actor="api",
                outcome="served",
                metadata_json={"entries": len(timeline)},
            )
        return timeline

    def get_state_diffs(self, trace_id: UUID) -> list[StateDiffEntryView]:
        state_diffs = self.repository.build_state_diffs(trace_id)
        if state_diffs:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="query.state_diff",
                actor="api",
                outcome="served",
                metadata_json={"entries": len(state_diffs)},
            )
        return state_diffs

    def get_claim_flow(self, trace_id: UUID) -> list[ClaimEvidenceFlowView]:
        claim_flow = self.repository.build_claim_flows(trace_id)
        if claim_flow:
            self.repository.record_audit_event(
                trace_id=trace_id,
                event_type="query.claim_flow",
                actor="api",
                outcome="served",
                metadata_json={"claims": len(claim_flow)},
            )
        return claim_flow
