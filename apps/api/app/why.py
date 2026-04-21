from __future__ import annotations

import re
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid5

from packages.schema.flight_recorder_schema import (
    ClaimRecord,
    ClaimVerificationStatus,
    EntityKind,
    EvidenceEdgeRecord,
    EvidenceGrade,
    ExplanationRecord,
    RawArtifactPayload,
    TraceBundleView,
)

MAX_EXTRACTED_CLAIMS = 5


def ensure_why_records(
    bundle: TraceBundleView,
    raw_artifacts: list[RawArtifactPayload] | None = None,
) -> TraceBundleView:
    if bundle.claims:
        return bundle

    raw_artifacts = raw_artifacts or []
    extracted_claims = _extract_claim_texts(bundle, raw_artifacts)
    if not extracted_claims:
        return bundle

    enriched = bundle.model_copy(deep=True)
    claims: list[ClaimRecord] = []
    edges: list[EvidenceEdgeRecord] = list(enriched.evidence_edges)
    explanations: list[ExplanationRecord] = list(enriched.explanations)

    output_artifact = _find_output_artifact(enriched)
    response_step = _find_response_step(enriched)
    now = _bundle_created_at(enriched)

    for index, claim_text in enumerate(extracted_claims):
        claim_id = _stable_uuid("claim", enriched.trace.id, index)
        claim = ClaimRecord(
            id=claim_id,
            trace_id=enriched.trace.id,
            claim_text=claim_text,
            claim_type=_classify_claim(claim_text),
            confidence=0.35,
            position_index=index,
            verification_status=ClaimVerificationStatus.UNSUPPORTED,
            metadata_json={
                "derived_from": "final_output",
                "extraction_method": "heuristic_sentence_split",
            },
            created_at=now,
        )
        claims.append(claim)

        support_edge_ids: list[UUID] = []
        if output_artifact is not None:
            artifact_edge = EvidenceEdgeRecord(
                id=_stable_uuid("edge-artifact", claim_id),
                from_kind=EntityKind.CLAIM,
                from_id=claim_id,
                to_kind=EntityKind.ARTIFACT,
                to_id=output_artifact.id,
                relation="stated_in_output",
                weight=0.4,
                metadata_json={"grade": EvidenceGrade.SELF_REPORTED.value},
                created_at=now,
            )
            edges.append(artifact_edge)
            support_edge_ids.append(artifact_edge.id)

        if response_step is not None:
            step_edge = EvidenceEdgeRecord(
                id=_stable_uuid("edge-step", claim_id),
                from_kind=EntityKind.CLAIM,
                from_id=claim_id,
                to_kind=EntityKind.STEP,
                to_id=response_step.id,
                relation="stated_in",
                weight=0.3,
                metadata_json={"grade": EvidenceGrade.SELF_REPORTED.value},
                created_at=now,
            )
            edges.append(step_edge)

        explanations.append(
            ExplanationRecord(
                id=_stable_uuid("explanation", claim_id),
                claim_id=claim_id,
                grade=EvidenceGrade.SELF_REPORTED,
                method="final_output_extraction",
                summary=(
                    "This claim was extracted from the model output and is not yet "
                    "supported by observed evidence."
                ),
                supporting_edge_ids=support_edge_ids,
                confidence=0.35,
                metadata_json={"unsupported_flag": True},
                created_at=now,
            )
        )

    return enriched.model_copy(
        update={
            "claims": claims,
            "evidence_edges": edges,
            "explanations": explanations,
        }
    )


def _extract_claim_texts(
    bundle: TraceBundleView,
    raw_artifacts: list[RawArtifactPayload],
) -> list[str]:
    output_text = _raw_output_text(bundle, raw_artifacts)
    if not output_text:
        response_step = _find_response_step(bundle)
        output_text = response_step.summary if response_step is not None else ""
    if not output_text:
        return []

    normalized = output_text.replace("\r\n", "\n")
    bullet_lines = [
        line.strip()[2:].strip()
        for line in normalized.splitlines()
        if line.strip().startswith("- ")
    ]
    candidates = bullet_lines or re.split(r"(?<=[.!?])\s+", normalized)

    claims: list[str] = []
    for candidate in candidates:
        cleaned = _normalize_claim(candidate)
        if cleaned and cleaned not in claims:
            claims.append(cleaned)
        if len(claims) >= MAX_EXTRACTED_CLAIMS:
            break
    return claims


def _raw_output_text(
    bundle: TraceBundleView,
    raw_artifacts: list[RawArtifactPayload],
) -> str:
    artifact = _find_output_artifact(bundle)
    if artifact is None:
        return ""
    payload = next(
        (item for item in raw_artifacts if item.artifact_id == artifact.id and item.text_content),
        None,
    )
    return payload.text_content or "" if payload is not None else ""


def _find_output_artifact(bundle: TraceBundleView):
    return next(
        (
            artifact
            for artifact in bundle.artifacts
            if artifact.source_type == "final_output" or artifact.source_system == "agent"
        ),
        None,
    )


def _find_response_step(bundle: TraceBundleView):
    return next(
        (
            step
            for step in sorted(bundle.steps, key=lambda item: item.step_index, reverse=True)
            if step.step_type == "response_synthesis" or step.metadata_json.get("final_output")
        ),
        None,
    )


def _normalize_claim(candidate: str) -> str:
    cleaned = re.sub(r"^#+\s*", "", candidate.strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip("- ").strip()
    if len(cleaned) < 12:
        return ""
    return cleaned


def _classify_claim(claim_text: str) -> str:
    lowered = claim_text.lower()
    if any(token in lowered for token in ["must", "should", "recommend", "need to"]):
        return "recommendation"
    if any(token in lowered for token in ["because", "caused", "identified", "found"]):
        return "factual"
    return "analysis"


def _bundle_created_at(bundle: TraceBundleView) -> datetime:
    timestamps = [bundle.trace.created_at, bundle.session.created_at]
    return min(timestamps) if timestamps else datetime.now(UTC)


def _stable_uuid(kind: str, *parts: UUID | int) -> UUID:
    suffix = ":".join(str(part) for part in parts)
    return uuid5(NAMESPACE_URL, f"aeris:why:{kind}:{suffix}")
