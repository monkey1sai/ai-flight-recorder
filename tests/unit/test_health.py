from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_healthz_returns_expected_payload() -> None:
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "api",
        "evidence_grades": [
            "observed",
            "self_reported",
            "inferred",
            "verified",
        ],
    }

