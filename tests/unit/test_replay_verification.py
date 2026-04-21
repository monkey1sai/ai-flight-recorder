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
