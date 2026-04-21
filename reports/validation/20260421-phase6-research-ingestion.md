# Validation Report: Phase 6 Research Ingestion Slice

## Scope

Validate Product Phase 6 on top of the runnable MVP checkpoint:

- research ingestion migration for `research_sync_runs`, `research_sync_cursors`, and `research_documents`
- fixture-backed Drive / arXiv sync receipts with cursor and export-status provenance
- repository-backed corpus explorer and sync-run history
- worker sync helpers using the shared research service
- `/research` page rendering persisted corpus items and sync status through live API reads

## Commands run

```powershell
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_research_connector_sync.py tests/integration/test_api_operator_surfaces.py -q
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/smoke/test_operator_surfaces_assets.py -q
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check apps/api apps/web/lib apps/web/components apps/web/app/research workers tests packages/schema
node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans
docker-compose -f infra/compose/docker-compose.yml config
docker-compose -f infra/compose/docker-compose.yml up --build -d
Invoke-WebRequest http://localhost:8080/healthz | Select-Object -ExpandProperty StatusCode
Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/drive/sync?q=incident%20notes | Select-Object -ExpandProperty Content
Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/arxiv/sync?q=faithful%20explanations%20provenance | Select-Object -ExpandProperty Content
Invoke-WebRequest http://localhost:8080/api/v1/research/corpus | Select-Object -ExpandProperty Content
Invoke-WebRequest http://localhost:8080/api/v1/research/sync-runs | Select-Object -ExpandProperty Content
(Invoke-WebRequest http://localhost:3000/research).StatusCode
```

## Results

- `python -m pytest tests/unit/test_research_connector_sync.py tests/integration/test_api_operator_surfaces.py -q`
  Passed. `7 passed`. Covered connector sync provenance (`cursor`, `export_status`), research sync persistence, corpus query, sync-run listing, and existing operator surfaces.
- `python -m pytest tests/smoke/test_operator_surfaces_assets.py -q`
  Passed. `1 passed`. Verified the new migration, component, and validation note are part of the operator-surface contract.
- `ruff check apps/api apps/web/lib apps/web/components apps/web/app/research workers tests packages/schema`
  Passed.
- `pyright ... apps packages workers tests`
  Passed with `0 errors`.
- `npm run lint --workspace @aeris/web`
  Passed.
- `npm run typecheck --workspace @aeris/web`
  Passed.
- `docker-compose ... down -v --remove-orphans`
  Passed. Cleared prior Postgres/blob volumes so the new research migration was validated on a fresh DB.
- `docker-compose ... config`
  Passed.
- `docker-compose ... up --build -d`
  Passed. The stack rebuilt cleanly and the API bootstrapped with the new `0004_research_ingestion_surfaces.up.sql` migration applied.
- `GET /healthz`
  Passed with HTTP `200`.
- `POST /api/v1/research/drive/sync?q=incident notes`
  Passed with HTTP `200`. Returned a sync receipt with:
  - `source_type="drive"`
  - `cursor="drive-fixture:incident notes:1"`
  - `item_count=1`
- `POST /api/v1/research/arxiv/sync?q=faithful explanations provenance`
  Passed with HTTP `200`. Returned a sync receipt with:
  - `source_type="arxiv"`
  - `cursor="oai-fixture:faithful explanations provenance:1"`
  - `item_count=1`
- `GET /api/v1/research/corpus`
  Passed with HTTP `200`. Returned persisted corpus items for both Drive and arXiv with:
  - `source_id`
  - `source_uri`
  - `retrieved_at`
  - `query`
  - `cursor`
  - `checksum`
  - `export_status`
- `GET /api/v1/research/sync-runs`
  Passed with HTTP `200`. Returned persisted sync-run history including `cursor_in`, `connector_mode`, and source-specific metadata (`export_format` or `harvest_mode`).
- `GET /research`
  Passed with HTTP `200`. The page rendered live connector sections plus the new corpus explorer and sync status panels, and its server-side sync step populated corpus data on first load.

## Failures

- None in the validated Phase 6 slice.

## Risk assessment

- Low product risk: the slice is fixture/mock-backed and keeps source provenance explicit instead of inventing richer evidence than the repo can prove.
- Medium operational risk: `/research` now performs server-side sync before reading the corpus, so repeated page loads will create repeated sync-run records until deduplication or scheduling rules are added.
- Medium roadmap risk: real Drive OAuth, Docs export, and arXiv OAI-PMH harvesting are still out of scope; this slice proves the single-db storage/query contract, not live credentials.

## Recommendation

`ready_to_merge`

Reason:
- schema, repository, API, worker, web, and validation evidence are all present
- the feature is runnable on a fresh compose stack
- provenance fields required by the plan are preserved in the persisted corpus

## Follow-up items

- Add connector-specific deduplication or schedule policy so repeated `/research` loads do not create redundant sync runs.
- Replace fixture connectors with credentialed implementations while keeping the same repository/API contract.
- If Docs export or OAI-PMH harvesting becomes real, preserve the current `cursor` / `export_status` / `query` fields rather than introducing opaque sync metadata.
