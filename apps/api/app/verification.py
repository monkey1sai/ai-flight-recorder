from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from packages.schema.flight_recorder_schema import (
    EvidenceGrade,
    ReplayRunRecord,
    ReplayVerificationView,
    TraceBundleView,
    VerificationRecord,
)


def derive_replay_verification(bundle: TraceBundleView) -> ReplayVerificationView:
    records: list[VerificationRecord] = []
    replay_trace_ids: set[UUID] = set()

    for claim in sorted(bundle.claims, key=lambda item: item.position_index):
        explanations = [
            explanation
            for explanation in bundle.explanations
            if explanation.claim_id == claim.id and explanation.grade == EvidenceGrade.VERIFIED
        ]
        for explanation in explanations:
            replay_trace_id = _parse_uuid(
                explanation.metadata_json.get("replay_trace_id")
                if explanation.metadata_json
                else None
            )
            if replay_trace_id is not None:
                replay_trace_ids.add(replay_trace_id)
            records.append(
                VerificationRecord(
                    id=_stable_uuid("verification", bundle.trace.id, claim.id, explanation.id),
                    trace_id=bundle.trace.id,
                    claim_id=claim.id,
                    claim_text=claim.claim_text,
                    explanation_id=explanation.id,
                    verification_status=claim.verification_status,
                    evidence_grade=explanation.grade,
                    verification_badge="replay_verified"
                    if replay_trace_id is not None
                    else "verified_without_replay_ref",
                    method=explanation.method,
                    summary=explanation.summary,
                    confidence=explanation.confidence or claim.confidence,
                    replay_trace_id=replay_trace_id,
                    supporting_edge_ids=list(explanation.supporting_edge_ids),
                    metadata_json={
                        **explanation.metadata_json,
                        "derived_from": "verified_explanation",
                    },
                    created_at=explanation.created_at,
                )
            )

    verified_claim_ids = {record.claim_id for record in records}
    methods = sorted({record.method for record in records}) if records else ["no_replay_evidence"]
    run = ReplayRunRecord(
        id=_stable_uuid("replay-run", bundle.trace.id),
        trace_id=bundle.trace.id,
        status="completed",
        method=methods[0] if len(methods) == 1 else "mixed",
        frame_count=len(bundle.steps),
        verified_claim_count=len(verified_claim_ids),
        started_at=_bundle_started_at(bundle),
        completed_at=_bundle_completed_at(bundle),
        metadata_json={
            "derived_from": "verified_explanations",
            "replay_trace_ids": [str(item) for item in sorted(replay_trace_ids, key=str)],
        },
    )
    return summarize_replay_verification(
        trace_id=bundle.trace.id,
        claim_count=len(bundle.claims),
        replay_run=run,
        records=records,
    )


def summarize_replay_verification(
    trace_id: UUID,
    claim_count: int,
    replay_run: ReplayRunRecord | None,
    records: list[VerificationRecord],
) -> ReplayVerificationView:
    sorted_records = sorted(
        records,
        key=lambda item: (item.claim_text, item.created_at, str(item.id)),
    )
    replay_trace_ids = sorted(
        {record.replay_trace_id for record in sorted_records if record.replay_trace_id is not None},
        key=str,
    )
    confidence_candidates = [
        record.confidence for record in sorted_records if record.confidence is not None
    ]
    return ReplayVerificationView(
        trace_id=trace_id,
        claim_count=claim_count,
        verified_claim_count=len({record.claim_id for record in sorted_records}),
        verification_badge="replay_verified" if sorted_records else "no_replay_evidence",
        confidence=max(confidence_candidates) if confidence_candidates else None,
        replay_trace_ids=replay_trace_ids,
        replay_run=replay_run,
        verification_records=sorted_records,
    )


def _bundle_started_at(bundle: TraceBundleView) -> datetime:
    return min(bundle.session.started_at, bundle.trace.started_at)


def _bundle_completed_at(bundle: TraceBundleView) -> datetime:
    candidates = [
        value
        for value in [bundle.trace.ended_at, *(step.ended_at for step in bundle.steps)]
        if value is not None
    ]
    return max(candidates) if candidates else datetime.now(UTC)


def _parse_uuid(value: object) -> UUID | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return UUID(value)
    except ValueError:
        return None


def _stable_uuid(kind: str, *parts: UUID) -> UUID:
    suffix = ":".join(str(part) for part in parts)
    return uuid5(NAMESPACE_URL, f"aeris:verification:{kind}:{suffix}")
