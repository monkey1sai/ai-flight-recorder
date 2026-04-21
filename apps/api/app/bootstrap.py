from __future__ import annotations

import time
from pathlib import Path

from apps.api.app.repositories import PostgresTraceRepository
from apps.api.app.settings import AppSettings
from apps.api.app.storage import LocalBlobStore
from packages.schema.flight_recorder_schema import (
    NormalizedTraceBundleIngestRequest,
    RawArtifactPayload,
    TraceBundleView,
)
from packages.testkit import load_trace_bundle_fixture


def apply_migration_directory(
    repository: PostgresTraceRepository, migration_dir: Path
) -> list[Path]:
    applied: list[Path] = []
    repository.ensure_migration_table()
    for path in sorted(migration_dir.glob("*.up.sql")):
        if repository.has_migration(path.name):
            continue
        if _migration_already_materialized(repository, path.name):
            repository.record_migration(path.name)
            continue
        repository.execute_script(path.read_text(encoding="utf-8"))
        repository.record_migration(path.name)
        applied.append(path)
    return applied


def wait_for_database(repository: PostgresTraceRepository, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            repository.ping()
            return
        except Exception as exc:  # pragma: no cover - retry path depends on local infra timing
            last_error = exc
            time.sleep(1)
    if last_error is not None:
        raise last_error


def materialize_raw_artifacts(
    request: NormalizedTraceBundleIngestRequest,
    blob_store: LocalBlobStore,
) -> TraceBundleView:
    artifact_map = {
        artifact.id: artifact.model_copy(deep=True)
        for artifact in request.bundle.artifacts
    }

    for raw_payload in request.raw_artifacts:
        artifact = artifact_map.get(raw_payload.artifact_id)
        if artifact is None:
            continue

        write_result = _write_payload(blob_store, raw_payload)
        merged_metadata = dict(artifact.metadata_json)
        merged_metadata.update(raw_payload.metadata_json)
        merged_metadata["blob_size_bytes"] = write_result.size_bytes
        artifact_map[artifact.id] = artifact.model_copy(
            update={
                "storage_ref": write_result.storage_ref,
                "checksum": write_result.checksum,
                "mime_type": raw_payload.mime_type or artifact.mime_type,
                "metadata_json": merged_metadata,
            }
        )

    return request.bundle.model_copy(update={"artifacts": list(artifact_map.values())})


def build_demo_ingest_request(blob_seed_root: str = "demo") -> NormalizedTraceBundleIngestRequest:
    fixture_bundle = load_trace_bundle_fixture().model_copy(deep=True)
    raw_artifacts = [
        RawArtifactPayload(
            artifact_id=artifact.id,
            namespace=f"{blob_seed_root}/{artifact.source_type}",
            mime_type=artifact.mime_type,
            json_content={
                "source_uri": artifact.source_uri,
                "metadata": artifact.metadata_json,
            }
            if artifact.mime_type == "application/json"
            or artifact.source_type in {"arxiv_metadata", "drive_doc"}
            else None,
            text_content=(
                "# Incident Summary\n\n"
                "- Canonical schema first\n"
                "- Claim-centric evidence\n"
                "- Timeline preserved"
                if artifact.source_type == "final_output"
                else None
            ),
            metadata_json={"seeded_by": "bootstrap_demo"},
        )
        for artifact in fixture_bundle.artifacts
    ]
    return NormalizedTraceBundleIngestRequest(bundle=fixture_bundle, raw_artifacts=raw_artifacts)


def bootstrap_live_local_environment(
    settings: AppSettings,
    migration_dir: Path,
    seed_demo: bool,
) -> TraceBundleView | None:
    repository = PostgresTraceRepository(settings.database_url)
    wait_for_database(repository, settings.startup_db_timeout_seconds)
    apply_migration_directory(repository, migration_dir)

    if not seed_demo:
        return None

    blob_store = LocalBlobStore(settings.blob_storage_root)
    bundle = materialize_raw_artifacts(build_demo_ingest_request(), blob_store)
    repository.upsert_bundle(bundle)
    return bundle


def _write_payload(blob_store: LocalBlobStore, payload: RawArtifactPayload):
    identifier = str(payload.artifact_id)
    if payload.json_content is not None:
        return blob_store.put_json(payload.namespace, identifier, payload.json_content)
    return blob_store.put_text(
        payload.namespace,
        identifier,
        payload.text_content or "",
        suffix=_suffix_for_mime(payload.mime_type),
    )


def _suffix_for_mime(mime_type: str | None) -> str:
    mapping = {
        "application/json": ".json",
        "text/markdown": ".md",
        "text/plain": ".txt",
    }
    return mapping.get(mime_type or "", ".txt")


def _migration_already_materialized(
    repository: PostgresTraceRepository, migration_name: str
) -> bool:
    if migration_name == "0001_canonical_schema.up.sql":
        return repository.type_exists("evidence_grade") and repository.table_exists("sessions")
    if migration_name == "0002_governance_surfaces.up.sql":
        return repository.table_exists("audit_events") and repository.table_exists(
            "policy_rules"
        )
    if migration_name == "0003_cognitive_state_surfaces.up.sql":
        return repository.table_exists("tasks") and repository.table_exists(
            "state_snapshots"
        )
    return False
