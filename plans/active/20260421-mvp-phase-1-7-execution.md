# MVP Phase 1-7 Execution

## 1. Purpose / Big Picture

把目前 fixture-backed skeleton 推進成可在本地單機環境實際啟動、寫入、查詢、觀看的 MVP。這一輪的核心目標不是一次把所有 production hardening 做完，而是先打通 live baseline、canonical persistence、API-first web surfaces、以及 demo/validation contract，讓後續 phase 都能在可運行主線上增量演進。

成功的判斷標準：

- `docker compose -f infra/compose/docker-compose.yml up --build` 可以啟動主要 stack
- 可以執行 migration / seed / demo ingest
- Web 可以從 live API 讀到 traces，而不只依賴 fixture
- trace detail / state diff / why / replay / research 至少有 API-first read path
- 對外清楚區分 live-backed、fixture-backed、以及 fallback 行為

## 2. Scope

In scope
- 建立新的 ExecPlan 並依 milestone 更新
- 建立 Phase 1 live local baseline：runtime settings、migration/seed/bootstrap、compose baseline、開發文件
- 建立 Phase 2/3 live ingest + Postgres-backed trace/timeline/detail path
- 讓 Web 改為 API-first，fixture 只作 fallback
- 保留 research connector 的 fixture/mock 行為，但改走 live API surface
- 補最小 validation evidence 與 smoke/integration checks
- 在 runnable checkpoint 上增量實作 Product Phase 4：`tasks`、`plan_versions`、`state_snapshots`、cognitive query API、trace detail cognitive panels
- 在 cognitive-state slice 上增量實作 Product Phase 5：claim extraction fallback、claim-centric why API contract、why panel evidence/status clarity

Out of scope
- 完整 production-grade OTLP protobuf ingestion
- ClickHouse / graph DB / 多租戶治理
- 真實 Drive OAuth、真實 arXiv harvest 網路同步
- 完整企業級 authn/authz
- 把 Rust edge daemon 升級成正式 P0 runtime

Assumptions
- Python Edge SDK 可以先採 normalized ingest path，之後再補完整 Collector export 路徑
- object storage 在這輪先以 local blob store abstraction 落地，保留後續切換到 S3-compatible object store 的邊界
- repo 目前已有 canonical schema、fixture-backed API/UI、以及 compose skeleton，可直接升級

Constraints
- canonical schema 是 source of truth；OTel 只做 mapping/interchange
- raw content 與 metadata 必須分離
- 每個 explanation grade 必須顯式呈現
- 保持 diff 聚焦，避免 unrelated refactor

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `plans/active/20260417-canonical-schema-migrations.md`
- `plans/active/20260417-platform-slices-3-10.md`
- `docs/architecture/canonical-schema.md`
- `docs/architecture/operator-slices.md`

## 3. Repository context

Relevant files and directories
- `apps/api/app/`
- `apps/web/`
- `packages/schema/flight_recorder_schema/`
- `packages/testkit/`
- `infra/compose/`
- `infra/docker/`
- `infra/k8s/`
- `tests/`
- `scripts/`
- `reports/validation/`

Current repo state
- API / Web / replay / research / governance surfaces are fixture-backed
- compose already defines `postgres` / `minio` / `otel-collector`, but collector only exports to `debug`
- no runtime Postgres repository exists
- no migration runner / seed runner / demo bootstrap command exists
- web pages still import `apps/web/lib/mock-data.ts` directly

## 4. Success criteria

- live repository selection is explicit and environment-driven
- demo stack can be bootstrapped via documented commands
- a seeded or ingested trace is queryable through API and rendered in web timeline / detail pages
- why/replay/research pages fetch from API, with fixture fallback only when API is unavailable
- artifact raw content is stored outside canonical query tables and referenced via `storage_ref`
- at least one smoke/integration path covers ingest -> query -> replay consistency
- docs and validation notes describe what is live-backed vs fixture-backed

## 5. Milestones

### Milestone 0 - Execution contract
Goal
- establish the plan, milestone order, and technical boundary

Deliverables
- this ExecPlan

Validation method
- plan completeness against `.agent/PLANS.md`

### Milestone 1 - Live local baseline
Goal
- add runtime settings, migration/seed/bootstrap scripts, and compose-friendly local conventions

Deliverables
- settings/runtime helpers
- migration runner
- demo seed / bootstrap commands
- compose and docker updates
- docs for local bring-up

Validation method
- smoke scripts
- file/path checks

### Milestone 2 - Live persistence
Goal
- replace fixture-only ingest/read path with a Postgres-backed trace repository for canonical entities

Deliverables
- repository abstraction
- Postgres repository implementation
- blob-store abstraction
- ingest/query/replay service updates

Validation method
- integration tests
- local API test client checks

### Milestone 3 - API-first web surfaces
Goal
- convert timeline/detail/replay/research pages to API-first behavior

Deliverables
- web data client
- server-side fetch helpers
- fallback handling

Validation method
- TypeScript typecheck
- smoke route assertions

### Milestone 4 - Validation and handoff
Goal
- capture evidence, update docs, and leave a runnable checkpoint

Deliverables
- updated plan
- validation note
- developer-facing usage docs

Validation method
- `make smoke`
- targeted unit/integration/e2e checks

### Milestone 5 - P1 Cognitive state slice
Goal
- add the first live cognitive-state surfaces without reopening the baseline/runtime architecture

Deliverables
- migration for `tasks`, `plan_versions`, `state_snapshots`
- typed schema models and bundle/query surfaces
- normalized ingest assembly for task derivation, append-only plan history, and state snapshots
- query API for task view and plan history
- trace detail UI for task summary and plan history

Validation method
- targeted unit/integration tests for derivation and query surfaces
- web typecheck
- compose-backed API/Web smoke against the seeded trace

### Milestone 6 - Claim-centric why v1
Goal
- make why surfaces claim-centric even when the incoming trace bundle does not provide precomputed claims

Deliverables
- why derivation fallback for claimless bundles
- safe default claim verification behavior (`unsupported` / `self_reported`) when no observed evidence exists
- why panel UI updates for confidence, evidence links, and unsupported flags
- validation evidence that live ingest does not overclaim unsupported output as supported

Validation method
- targeted unit/integration tests for claim extraction fallback
- repo lint/typecheck
- compose-backed live ingest of a claimless trace plus `claim-evidence` verification

### Milestone 7 - Research ingestion slice
Goal
- persist fixture-backed Drive/arXiv sync results into the single Postgres MVP store and expose a runnable corpus explorer

Deliverables
- migration for `research_sync_runs`, `research_sync_cursors`, and `research_documents`
- typed schema and repository methods for corpus items, sync runs, and cursors
- fixture connector sync receipts with cursor / export status provenance
- API endpoints for sync, corpus listing, and sync-run history
- `/research` page updated to show persisted corpus and sync status after server-side sync

Validation method
- targeted unit/integration tests for connector sync metadata and corpus persistence
- repo lint/typecheck
- compose-backed API/Web smoke for `/api/v1/research/*` and `/research`

## 6. Progress

- [x] 2026-04-21 08:08 UTC reread repo instructions, relevant active plans, architecture docs, current runtime files, and web/API fixture surfaces
- [x] 2026-04-21 08:18 UTC created this ExecPlan to drive the MVP implementation work
- [x] 2026-04-21 09:02 UTC Milestone 1 completed: added runtime settings, local blob-store convention, bootstrap scripts, compose updates, and a second migration slice for governance surfaces
- [x] 2026-04-21 09:11 UTC Milestone 2 completed: repository abstraction, Postgres-backed trace repository, normalized ingest endpoint, and minimal Python edge SDK demo path landed
- [x] 2026-04-21 09:18 UTC Milestone 3 completed: timeline, trace detail, replay, research, admin, and home page now prefer live API reads with fixture fallback
- [x] 2026-04-21 09:27 UTC Milestone 4 completed: added validation coverage, updated docs, and wrote `reports/validation/20260421-mvp-live-local-baseline.md`
- [x] 2026-04-21 07:51 UTC reran Milestone 4 as runnable validation / handoff: `docker-compose up --build -d` succeeded, demo ingest succeeded, API returned live trace data, and Web routes `/`, `/timeline`, `/traces/[id]`, `/replay/[id]`, `/research`, `/admin` all returned HTTP 200
- [x] 2026-04-21 08:03 UTC Milestone 5 completed: shipped Product Phase 4 cognitive-state storage, derivation, query API, trace detail panels, and compose-backed validation evidence in `reports/validation/20260421-p1-cognitive-state-slice.md`
- [x] 2026-04-21 08:23 UTC Milestone 6 completed: shipped claim extraction fallback, claim-centric why panel updates, and compose-backed proof that a claimless live ingest becomes `unsupported` + `self_reported` instead of being upgraded to supported; validation captured in `reports/validation/20260421-claim-centric-why-v1.md`
- [x] 2026-04-21 09:58 UTC Milestone 7 completed: shipped research ingestion tables, fixture-backed sync receipts with cursor/export provenance, repository-backed corpus query APIs, worker sync helpers, and a persisted corpus explorer on `/research`; validation captured in `reports/validation/20260421-phase6-research-ingestion.md`

## 7. Research notes

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 18
  Finding: canonical schema must remain internal truth, with OTel acting as mapping/export layer.
  Why it matters: runtime persistence should target canonical entities directly; collector compatibility is a separate layer.
  Confidence: high

- Source: `docs/architecture/canonical-schema.md`
  Finding: the first migration already covers the core observability entities needed for a live ingest/read slice.
  Why it matters: Milestone 2 can focus on a repository implementation instead of inventing a second schema.
  Confidence: high

## 8. Surprises & Discoveries

- The compose baseline already includes `postgres`, `minio`, and `otel-collector`, but the API runtime does not yet have a DB or blob persistence implementation.
- The web app is structurally ready for API-first migration because the current pages already mirror API route shapes one-to-one.
- There is no repo-local Postgres driver dependency declared today, so the live repository implementation must also establish a durable runtime dependency convention.
- The direct script path (`python scripts/bootstrap_local.py`) initially failed because repo-root imports were not on `sys.path`; the scripts now self-bootstrap their import path before doing any work.
- `docker-compose ... config` succeeds in this shell, but `bootstrap_local.py` still correctly blocks on the absence of a running Postgres instance when executed outside Docker.
- Runnable validation exposed concrete infra/runtime blockers that had to be fixed before handoff: an invalid MinIO tag, Windows Docker build context pollution without `.dockerignore`, unpublished `vendor/npm` tarballs in the web image, host port collision on `5432`, ingest ordering that violated the `observations -> artifacts` foreign key, migration replay on container restart, and Next 16 dynamic-route `params` compatibility for `/traces/[id]` and `/replay/[id]`.
- Product Phase 4 could be added without changing the ingest API contract: the normalized bundle path was sufficient once the repo derived missing cognitive records (`task`, `plan_versions`, `state_snapshots`) at the persistence boundary.
- The seeded demo trace did not carry explicit cognitive records, so the repository and fixture fallback now derive them deterministically from the existing `trace`, `steps`, and `state_deltas` instead of requiring fixture JSON rewrites.
- Product Phase 5 also fit the same additive pattern: claim extraction fallback could run at ingest time without introducing a separate why endpoint or changing the edge SDK contract.
- Live compose validation exposed a circular foreign-key insertion issue between `tasks.trace_id` and `traces.task_id`; the fix was a two-phase trace upsert (`task_id = null` first, then backfill after task insert).
- Research Phase 6 initially exposed a contract problem: making `GET /research/*/search` persist corpus data caused a semantic mismatch and duplicated sync runs. The final slice keeps `search` read-only and uses dedicated `POST /sync` endpoints plus server-side sync on the `/research` page.
- Because `/research` is a server component, loading search and corpus in parallel on first render produced an empty corpus race. The page now syncs first, then reads catalog/corpus/status.

## 9. Decision log

- 2026-04-21: implement the MVP on top of the existing fixture-backed skeleton instead of replacing it wholesale.
  Rationale: this preserves a reliable fallback while progressively turning on live-backed behavior.
  Alternatives rejected: rewriting all services and pages from scratch.

- 2026-04-21: prioritize local baseline + live persistence + API-first read path before deeper research/replay hardening.
  Rationale: the repository currently lacks a runnable live vertical slice; that gap blocks every later phase.
  Alternatives rejected: starting with task/plan/research tables before a stable live path exists.

- 2026-04-21: keep the live demo blob store filesystem-backed for this checkpoint.
  Rationale: it creates a durable raw-content separation immediately without introducing extra S3 client dependencies into the first live slice.
  Alternatives rejected: wiring MinIO client logic in the same checkpoint; keeping raw content inline in DB rows.

- 2026-04-21: implement Product Phase 4 as an additive slice on top of the normalized ingest bundle instead of introducing a second ingest contract.
  Rationale: the runnable checkpoint already proves the bundle path; adding optional/derived cognitive records keeps the diff focused and preserves the existing demo flow.
  Alternatives rejected: creating a separate cognitive-only ingest endpoint or requiring all emitters to send `tasks`/`plan_versions`/`state_snapshots` immediately.

- 2026-04-21: derive the first task title and summary from existing trace/step metadata when explicit task payload is absent.
  Rationale: the current demo flow already has plan and state data, so deterministic derivation is enough for MVP cognitive observability and keeps emitters backward-compatible.
  Alternatives rejected: blocking the feature on a new edge SDK payload shape.

- 2026-04-21: for claimless bundles, extract claims from final output text and default them to `verification_status=unsupported` with a `self_reported` explanation.
  Rationale: Phase 5 requires claim-centric why records, but the MVP must not overclaim unsupported outputs as observed or verified evidence.
  Alternatives rejected: synthesizing `supported` claims from weak heuristics; delaying why generation until richer connectors arrive.

- 2026-04-21: keep research sync side effects behind explicit `POST /sync` routes and let `/research` call them server-side before loading the corpus.
  Rationale: this preserves correct HTTP semantics and avoids pretending a read-only search request is mutation-free while still letting the page render persisted corpus data on first load.
  Alternatives rejected: mutating storage from `GET /search`; leaving `/research` empty until a separate manual sync step runs.

## 10. Validation plan

- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/e2e -q`
- `uv run python -m pytest tests/smoke -q`
- `uv run ruff check .`
- `node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests`
- `npm run typecheck --workspace @aeris/web`
- `npm run lint --workspace @aeris/web`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `docker-compose -f infra/compose/docker-compose.yml config`
- `docker-compose -f infra/compose/docker-compose.yml up --build -d`
- `uv run python scripts/emit_demo_trace.py`
- `Invoke-WebRequest http://localhost:8080/healthz`
- `Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222`
- `Invoke-WebRequest http://localhost:3000/`
- `Invoke-WebRequest http://localhost:3000/timeline`
- `Invoke-WebRequest http://localhost:3000/traces/22222222-2222-4222-8222-222222222222`
- `Invoke-WebRequest http://localhost:3000/replay/22222222-2222-4222-8222-222222222222`
- `Invoke-WebRequest http://localhost:3000/research`
- `Invoke-WebRequest http://localhost:3000/admin`
- `uv run python scripts/bootstrap_local.py`
- cognitive-state follow-up:
  `uv run python -m pytest tests/unit tests/integration -q`
  `npm run typecheck --workspace @aeris/web`
  `docker-compose -f infra/compose/docker-compose.yml up --build -d`
  `Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222/task`
  `Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222/plan-history`
  `Invoke-WebRequest http://localhost:3000/traces/22222222-2222-4222-8222-222222222222`
  `uv run python scripts/emit_demo_trace.py`
- claim-centric why follow-up:
  `uv run python -m pytest tests/unit/test_why_derivation.py tests/integration/test_api_operator_surfaces.py -q`
  `uv run python -m pytest tests/unit tests/integration tests/smoke -q`
  `uv run ruff check .`
  `node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests`
  `npm run lint --workspace @aeris/web`
  `npm run typecheck --workspace @aeris/web`
  `docker-compose -f infra/compose/docker-compose.yml up --build -d api web`
  live POST of a claimless normalized trace bundle to `/api/v1/ingest/normalized-trace-bundles`
  `Invoke-WebRequest http://localhost:8080/api/v1/traces/{trace_id}/claim-evidence`
  `Invoke-WebRequest http://localhost:3000/traces/{trace_id}`
- research ingestion follow-up:
  `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_research_connector_sync.py tests/integration/test_api_operator_surfaces.py -q`
  `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/smoke/test_operator_surfaces_assets.py -q`
  `C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check apps/api apps/web/lib apps/web/components apps/web/app/research workers tests packages/schema`
  `node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests`
  `npm run lint --workspace @aeris/web`
  `npm run typecheck --workspace @aeris/web`
  `docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans`
  `docker-compose -f infra/compose/docker-compose.yml config`
  `docker-compose -f infra/compose/docker-compose.yml up --build -d`
  `Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/drive/sync?q=incident%20notes`
  `Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/arxiv/sync?q=faithful%20explanations%20provenance`
  `Invoke-WebRequest http://localhost:8080/api/v1/research/corpus`
  `Invoke-WebRequest http://localhost:8080/api/v1/research/sync-runs`
  `Invoke-WebRequest http://localhost:3000/research`

## 11. Risks / Blockers

- A durable Postgres runtime dependency must be added without destabilizing the existing local environment.
- Full OTLP protobuf ingest may remain out of scope for this checkpoint; the implementation must not overclaim collector completeness.
- Current branch contains unrelated untracked local directories (`.codex/`, `.worktrees/`, `graphify-out/`, `總覽.md`) that must stay untouched.

## 12. Deliverables

- `plans/active/20260421-mvp-phase-1-7-execution.md`
- runtime settings / repository / storage / script changes
- API and web updates for live-backed slices
- updated docs and validation report

## 13. Completion note

Shipped
- local runtime settings and repository auto-selection
- filesystem-backed blob materialization for normalized ingest
- Postgres-backed trace repository for canonical observability entities plus governance tables
- API-first web data adapter with fixture fallback
- bootstrap / emit-demo scripts and minimal Python edge SDK
- runnable validation evidence in `reports/validation/20260421-mvp-live-local-baseline.md`, including compose bring-up, demo ingest, API checks, and Web route checks

Did not ship
- full OTLP protobuf ingest through the collector into the API
- live Google Drive / arXiv sync credentials
- long-running edge daemon behavior beyond the current one-shot skeleton
- multi-task per trace orchestration or richer explicit task payloads from the edge
- dedicated `state_snapshots` query UI outside trace detail
- observed-evidence auto-linking beyond conservative `self_reported` fallback for claimless traces
- real credentialed Drive sync, docs export, and arXiv OAI-PMH harvest; Phase 6 persists the fixture/mock contract only

Follow-up
- if Phase 5 starts, build on the now-verified runnable checkpoint and cognitive-state slice instead of reopening baseline work
- if later why iterations need stronger support statuses, add them via provenance-aware matching or replay evidence instead of lexical guesswork
- replace the local blob-store implementation with S3-compatible storage when the MVP needs shared object storage
- decide whether future edge emitters should send explicit task / plan payloads or continue relying on repository-side derivation
