from apps.api.app.why import ensure_why_records
from packages.schema.flight_recorder_schema import RawArtifactPayload
from packages.testkit import load_trace_bundle_fixture


def test_why_derivation_extracts_claims_from_final_output_when_missing() -> None:
    bundle = load_trace_bundle_fixture().model_copy(
        deep=True,
        update={
            "claims": [],
            "evidence_edges": [],
            "explanations": [],
        },
    )
    output_artifact = next(
        artifact for artifact in bundle.artifacts if artifact.source_type == "final_output"
    )
    request_payloads = [
        RawArtifactPayload(
            artifact_id=output_artifact.id,
            namespace="demo/final_output",
            mime_type="text/markdown",
            text_content=(
                "# Incident Summary\n\n"
                "- The deployment manifest is stale and requires review.\n"
                "- Human review is required before remediation.\n"
            ),
        )
    ]

    enriched = ensure_why_records(bundle, request_payloads)

    assert len(enriched.claims) == 2
    assert all(claim.verification_status == "unsupported" for claim in enriched.claims)
    assert all(explanation.grade == "self_reported" for explanation in enriched.explanations)
    assert any(edge.relation == "stated_in_output" for edge in enriched.evidence_edges)
