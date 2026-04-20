# Operator Slices 3 Through 10

## Purpose

這份文件描述 repo 目前為了覆蓋 task items `3` 到 `10` 所建立的第一個整合骨架：API、web、edge daemon、connectors、governance、e2e tests 與 deployment manifests 都以同一份 fixture-backed contract 對齊。

## Shared contract

- canonical entity models 仍在 `packages/schema/flight_recorder_schema/canonical.py`
- operator-facing aggregate / governance / research models 在 `packages/schema/flight_recorder_schema/surfaces.py`
- shared fixtures 在 `packages/testkit/fixtures/`
- Python loader 在 `packages/testkit/fixture_loader.py`

## API slices

`apps/api/app/` 目前分成：

- `routers/ingest.py`
- `routers/query.py`
- `routers/replay.py`
- `routers/research.py`
- `routers/admin.py`
- `repositories/fixture_store.py`
- `services/`
- `connectors/`

目前是 fixture-backed，而不是 live Postgres-backed；目的在於先穩定 route shape、claim/evidence flow、governance metadata 與 replay contract。

## Web slices

`apps/web` 已提供：

- `/timeline`
- `/traces/[traceId]`
- `/replay/[traceId]`
- `/research`
- `/admin`

所有頁面都直接使用 shared fixture contract，避免 UI 自己再發明另一套 trace shape。

## Edge daemon

`edge/daemon` 是第一版 Rust skeleton，提供這些模組邊界：

- `config.rs`
- `policy.rs`
- `spool.rs`
- `blob.rs`
- `otlp.rs`
- `health.rs`

目前沒有接 live telemetry 或 blob store，但已把 policy evaluation、blob staging、spool queue 與 export preview 分開。

## Research connectors

Drive 與 arXiv 目前是 fixture connector：

- `apps/api/app/connectors/drive.py`
- `apps/api/app/connectors/arxiv.py`
- `workers/drive_sync/job.py`
- `workers/arxiv_sync/job.py`

保留的 provenance 欄位至少包含：

- `source_type`
- `source_id`
- `source_uri`
- `retrieved_at`
- `query`
- `license_or_terms_note`
- `checksum`

## Governance

governance 目前先以 API surface 建立：

- audit events
- policy rules
- retention policies

API 路由為 `/api/v1/admin/snapshot`，web 對應 `/admin`。

## Deployment

baseline manifests 位於：

- `infra/docker/`
- `infra/compose/docker-compose.yml`
- `infra/k8s/`

這些 manifests 主要用來固定 service boundary：`api`、`web`、`edge-daemon`、`postgres`、`redis`、`minio`、`otel-collector`。

## Known limitations

- 無 live Postgres persistence
- 無 live Google Drive / arXiv credentials
- 無 browser-based Playwright execution
- Node / Python deps 仍受目前環境阻塞，靜態驗證優先
