from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from apps.api.app.bootstrap import build_demo_ingest_request
from apps.api.app.dependencies import (
    get_blob_store,
    get_governance_service,
    get_replay_service,
    get_repository,
    get_research_service,
    get_trace_workbench_service,
)
from apps.api.app.main import app
from apps.api.app.settings import get_settings

client = TestClient(app)


def test_trace_query_surfaces_return_seeded_contract() -> None:
    traces_response = client.get("/api/v1/traces")
    timeline_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/timeline"
    )
    task_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/task"
    )
    plan_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/plan-history"
    )
    claim_response = client.get(
        "/api/v1/traces/22222222-2222-4222-8222-222222222222/claim-evidence"
    )

    assert traces_response.status_code == 200
    assert timeline_response.status_code == 200
    assert task_response.status_code == 200
    assert plan_response.status_code == 200
    assert claim_response.status_code == 200
    assert traces_response.json()[0]["trace_kind"] == "agent_run"
    assert task_response.json()["task"]["title"]
    assert task_response.json()["plan_revision_count"] >= 1
    assert plan_response.json()[0]["revision"] >= 0
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


def test_research_sync_persists_corpus_and_cursor(monkeypatch) -> None:
    monkeypatch.setenv("AERIS_REPOSITORY_BACKEND", "fixture")
    _clear_dependency_caches()

    drive_sync = client.post("/api/v1/research/drive/sync?q=incident notes")
    arxiv_sync = client.post(
        "/api/v1/research/arxiv/sync?q=faithful explanations provenance"
    )
    corpus_response = client.get("/api/v1/research/corpus?q=provenance")
    sync_runs_response = client.get("/api/v1/research/sync-runs?source_type=arxiv")

    assert drive_sync.status_code == 200
    assert arxiv_sync.status_code == 200
    assert drive_sync.json()["cursor"].startswith("drive-fixture:")
    assert arxiv_sync.json()["cursor"].startswith("oai-fixture:")
    assert corpus_response.status_code == 200
    assert sync_runs_response.status_code == 200
    assert any(
        item["provenance"]["source_type"] == "arxiv"
        and item["provenance"]["cursor"].startswith("oai-fixture:")
        and item["provenance"]["export_status"] == "metadata_only"
        for item in corpus_response.json()["items"]
    )
    assert sync_runs_response.json()[0]["source_type"] == "arxiv"

    _clear_dependency_caches()


def test_normalized_ingest_materializes_blob_refs(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AERIS_REPOSITORY_BACKEND", "fixture")
    monkeypatch.setenv("BLOB_STORAGE_ROOT", str(tmp_path))
    _clear_dependency_caches()

    request = build_demo_ingest_request()
    response = client.post(
        "/api/v1/ingest/normalized-trace-bundles",
        json=request.model_dump(mode="json"),
    )
    detail_response = client.get(f"/api/v1/traces/{request.bundle.trace.id}")

    assert response.status_code == 200
    assert detail_response.status_code == 200
    artifact_refs = [item["storage_ref"] for item in detail_response.json()["artifacts"]]
    assert any(ref.startswith("file:///") for ref in artifact_refs)
    assert any(tmp_path.rglob("*"))

    _clear_dependency_caches()


def test_normalized_ingest_derives_unsupported_why_records_when_claims_absent(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("AERIS_REPOSITORY_BACKEND", "fixture")
    monkeypatch.setenv("BLOB_STORAGE_ROOT", str(tmp_path))
    _clear_dependency_caches()

    request = build_demo_ingest_request()
    session_id = uuid4()
    trace_id = uuid4()
    step_ids = [uuid4() for _ in request.bundle.steps]
    artifact_ids = [uuid4() for _ in request.bundle.artifacts]
    step_id_map = {
        step.id: step_ids[index] for index, step in enumerate(request.bundle.steps)
    }
    artifact_id_map = {
        artifact.id: artifact_ids[index] for index, artifact in enumerate(request.bundle.artifacts)
    }
    request.bundle = request.bundle.model_copy(
        deep=True,
        update={
            "session": request.bundle.session.model_copy(update={"id": session_id}),
            "trace": request.bundle.trace.model_copy(
                update={"id": trace_id, "session_id": session_id}
            ),
            "steps": [
                step.model_copy(
                    update={
                        "id": step_id_map[step.id],
                        "trace_id": trace_id,
                    }
                )
                for step in request.bundle.steps
            ],
            "observations": [
                observation.model_copy(
                    update={
                        "step_id": step_id_map[observation.step_id],
                        "source_artifact_id": artifact_id_map[observation.source_artifact_id]
                        if observation.source_artifact_id is not None
                        else None,
                    }
                )
                for observation in request.bundle.observations
            ],
            "state_deltas": [
                delta.model_copy(update={"step_id": step_id_map[delta.step_id]})
                for delta in request.bundle.state_deltas
            ],
            "artifacts": [
                artifact.model_copy(update={"id": artifact_id_map[artifact.id]})
                for artifact in request.bundle.artifacts
            ],
            "interventions": [
                intervention.model_copy(
                    update={
                        "trace_id": trace_id,
                        "step_id": step_id_map[intervention.step_id]
                        if intervention.step_id is not None
                        else None,
                    }
                )
                for intervention in request.bundle.interventions
            ],
            "evaluations": [
                evaluation.model_copy(update={"trace_id": trace_id})
                for evaluation in request.bundle.evaluations
            ],
            "claims": [],
            "evidence_edges": [],
            "explanations": [],
        },
    )
    request.raw_artifacts = [
        payload.model_copy(update={"artifact_id": artifact_id_map[payload.artifact_id]})
        for payload in request.raw_artifacts
    ]
    for payload in request.raw_artifacts:
        if payload.text_content:
            payload.text_content = (
                "# Incident Summary\n\n"
                "- The deployment manifest is stale.\n"
                "- Human review is required before remediation.\n"
            )

    response = client.post(
        "/api/v1/ingest/normalized-trace-bundles",
        json=request.model_dump(mode="json"),
    )
    claim_response = client.get(f"/api/v1/traces/{trace_id}/claim-evidence")

    assert response.status_code == 200
    assert claim_response.status_code == 200
    assert len(claim_response.json()) >= 1
    assert claim_response.json()[0]["verification_status"] == "unsupported"
    assert claim_response.json()[0]["explanations"][0]["grade"] == "self_reported"

    _clear_dependency_caches()


def _clear_dependency_caches() -> None:
    get_settings.cache_clear()
    get_blob_store.cache_clear()
    get_repository.cache_clear()
    get_trace_workbench_service.cache_clear()
    get_replay_service.cache_clear()
    get_governance_service.cache_clear()
    get_research_service.cache_clear()
