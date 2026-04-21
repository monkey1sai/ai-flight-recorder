from fastapi.testclient import TestClient

from apps.api.app.main import app
from packages.testkit import load_trace_bundle_fixture

client = TestClient(app)


def test_ingest_query_replay_flow_is_consistent() -> None:
    bundle = load_trace_bundle_fixture()

    ingest_response = client.post(
        "/api/v1/ingest/trace-bundles",
        json=bundle.model_dump(mode="json"),
    )
    detail_response = client.get(f"/api/v1/traces/{bundle.trace.id}")
    replay_response = client.get(f"/api/v1/replay/{bundle.trace.id}")
    replay_verification_response = client.get(
        f"/api/v1/replay/{bundle.trace.id}/verification"
    )
    admin_response = client.get(f"/api/v1/admin/snapshot?trace_id={bundle.trace.id}")

    assert ingest_response.status_code == 200
    assert detail_response.status_code == 200
    assert replay_response.status_code == 200
    assert replay_verification_response.status_code == 200
    assert admin_response.status_code == 200
    assert ingest_response.json()["trace_id"] == str(bundle.trace.id)
    assert detail_response.json()["trace"]["id"] == str(bundle.trace.id)
    assert len(replay_response.json()) == len(bundle.steps)
    assert replay_verification_response.json()["verified_claim_count"] >= 1
    assert len(admin_response.json()["audit_events"]) >= 1
