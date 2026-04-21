from fastapi.testclient import TestClient

from apps.api.app.main import app

client = TestClient(app)


def test_trace_query_surfaces_return_seeded_contract() -> None:
    traces_response = client.get("/api/v1/traces")
    timeline_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/timeline"
    )
    claim_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/claim-evidence"
    )

    assert traces_response.status_code == 200
    assert timeline_response.status_code == 200
    assert claim_response.status_code == 200
    assert traces_response.json()[0]["trace_kind"] == "agent_run"
    assert timeline_response.json()[0]["evidence_grade"] in {
        "observed",
        "self_reported",
        "inferred",
        "verified",
    }
    assert claim_response.json()[0]["verification_status"] in {
        "supported",
        "partially_supported",
        "unsupported",
        "model_prior_only",
        "conflicted",
    }


def test_research_and_admin_surfaces_expose_governance_metadata() -> None:
    drive_response = client.get("/api/v1/research/drive/search?q=incident notes")
    arxiv_response = client.get(
        "/api/v1/research/arxiv/search?q=faithful explanations provenance"
    )
    admin_response = client.get("/api/v1/admin/snapshot")

    assert drive_response.status_code == 200
    assert arxiv_response.status_code == 200
    assert admin_response.status_code == 200
    assert drive_response.json()["items"][0]["provenance"]["source_type"] == "drive"
    assert arxiv_response.json()["items"][0]["provenance"]["source_type"] == "arxiv"
    assert len(admin_response.json()["policies"]) >= 1
