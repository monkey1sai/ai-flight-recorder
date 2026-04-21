from apps.api.app.verification import derive_replay_verification
from packages.testkit import load_trace_bundle_fixture


def test_replay_verification_derivation_builds_replay_backed_summary() -> None:
    bundle = load_trace_bundle_fixture()

    verification = derive_replay_verification(bundle)

    assert verification.trace_id == bundle.trace.id
    assert verification.verification_badge == "replay_verified"
    assert verification.verified_claim_count == 1
    assert verification.claim_count == len(bundle.claims)
    assert verification.replay_run is not None
    assert verification.replay_run.frame_count == len(bundle.steps)
    assert verification.verification_records[0].verification_badge == "replay_verified"
    assert verification.verification_records[0].replay_trace_id is not None


def test_replay_verification_without_replay_trace_id_stays_non_replay_badged() -> None:
    bundle = load_trace_bundle_fixture()
    verified_explanation = next(
        item for item in bundle.explanations if item.grade.value == "verified"
    )
    bundle = bundle.model_copy(
        deep=True,
        update={
            "explanations": [
                item.model_copy(update={"metadata_json": {}})
                if item.id == verified_explanation.id
                else item
                for item in bundle.explanations
            ]
        },
    )

    verification = derive_replay_verification(bundle)

    assert verification.verification_badge == "verified_without_replay_ref"
    assert verification.replay_trace_ids == []
    assert verification.replay_run is None
    assert verification.verification_records[0].verification_badge == (
        "verified_without_replay_ref"
    )


def test_replay_verification_without_verified_explanations_has_no_run() -> None:
    bundle = load_trace_bundle_fixture()
    bundle = bundle.model_copy(
        deep=True,
        update={
            "explanations": [
                item for item in bundle.explanations if item.grade.value != "verified"
            ]
        },
    )

    verification = derive_replay_verification(bundle)

    assert verification.verification_badge == "no_replay_evidence"
    assert verification.verification_records == []
    assert verification.replay_run is None


def test_replay_verification_preserves_explicit_zero_confidence() -> None:
    bundle = load_trace_bundle_fixture()
    verified_explanation = next(
        item for item in bundle.explanations if item.grade.value == "verified"
    )
    claim = next(item for item in bundle.claims if item.id == verified_explanation.claim_id)
    bundle = bundle.model_copy(
        deep=True,
        update={
            "claims": [
                item.model_copy(update={"confidence": 0.91})
                if item.id == claim.id
                else item
                for item in bundle.claims
            ],
            "explanations": [
                item.model_copy(update={"confidence": 0.0})
                if item.id == verified_explanation.id
                else item
                for item in bundle.explanations
            ],
        },
    )

    verification = derive_replay_verification(bundle)

    assert verification.verification_records[0].confidence == 0.0
