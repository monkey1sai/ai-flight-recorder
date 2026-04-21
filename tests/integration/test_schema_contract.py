from uuid import uuid4

from packages.schema.flight_recorder_schema import EvidenceGrade, StepEnvelope


def test_step_envelope_serializes_bootstrap_contract() -> None:
    envelope = StepEnvelope(
        session_id=uuid4(),
        trace_id=uuid4(),
        step_id=uuid4(),
        evidence_grade=EvidenceGrade.OBSERVED,
        summary="Bootstrapped skeleton records the first validated step.",
        source_uri="repo://plans/active/20260417-bootstrap-monorepo.md",
    )

    dumped = envelope.model_dump(mode="json")

    assert dumped["evidence_grade"] == "observed"
    assert dumped["summary"].startswith("Bootstrapped skeleton")
    assert dumped["source_uri"] == "repo://plans/active/20260417-bootstrap-monorepo.md"

