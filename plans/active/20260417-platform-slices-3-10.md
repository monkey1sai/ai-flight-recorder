# Platform Slices 3 Through 10

## 1. Purpose / Big Picture

把 repo 從 schema-only skeleton 推進到第一個可串起來的 observability 平台切片。這一輪要交付可 ingest / query / replay 的 FastAPI、可對應 operator workflow 的 Next.js 頁面、可擴充的 edge Rust daemon skeleton、Drive / arXiv provenance connector skeleton、governance surfaces、e2e 測試骨架與 deployment manifests，讓下一輪可以直接往真實 persistence 與 live infra 擴充，而不是再重做邊界。

## 2. Scope

In scope
- 建立新的 active ExecPlan 並依 milestone 更新
- 擴充 `apps/api`：ingest / query / replay / research / admin API skeleton
- 建立 fixture-backed repository、state diff、claim/evidence flow、audit / policy / retention service
- 建立 `edge/daemon` Rust skeleton 與模組化 runtime 邊界
- 擴充 `apps/web`：timeline、trace detail、replay、research、admin 頁面與共享元件
- 建立 Drive / arXiv connector 與 worker skeleton
- 建立 e2e 測試骨架
- 建立 Docker / Compose / Kubernetes baseline manifests
- 更新 docs、README、validation report

Out of scope
- 真實 Postgres 寫入實作
- 真實 Redis / object store / queue runtime
- 真實 Google Drive OAuth 與 arXiv live network calls
- 真正的 browser Playwright execution
- production-ready authn / authz

Assumptions
- 這一輪以 fixture-backed slice 驗證 API / UI / governance contract
- 現在的環境無法可靠安裝 Python / Node 依賴，因此驗證會偏向 syntax、static contract、Rust cargo check 與 inline assertions
- 使用者要的是「逐步執行 3–10」，可接受先交付完整 skeleton 與 typed contract，再於後續 turn 接 live infra

Constraints
- 保持 append-only 與 provenance-first 設計
- 不修改 `.codex/`、`.agents/skills/`、既有 repo workflow infra
- 不把 `self_reported` 混成 `verified`
- 每個新增模組都要能在無外部憑證時以 fixture / mock 模式運作

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `plans/active/20260417-bootstrap-monorepo.md`
- `plans/active/20260417-canonical-schema-migrations.md`
- `docs/TASK_SEEDS.md`
- `docs/architecture/canonical-schema.md`

## 3. Repository context

Relevant files and directories
- `apps/api/app/`
- `apps/web/`
- `packages/schema/flight_recorder_schema/`
- `workers/`
- `tests/`
- `infra/`
- `docs/`

Current repo state
- `apps/api` 目前只有 bootstrap health endpoint
- `apps/web` 目前只有 landing shell
- canonical schema migration 與 typed models 已存在
- `workers/*` 只有 placeholder README
- `infra/` 目錄尚未建立
- e2e tests 與 deployment manifests 尚未存在

Planned touch surface
- `apps/api/app/**`
- `apps/web/**`
- `packages/schema/flight_recorder_schema/**`
- `workers/**`
- `edge/daemon/**`
- `tests/**`
- `infra/**`
- `docs/architecture/**`
- `README.md`
- `reports/validation/20260417-platform-slices-3-10.md`

## 4. Success criteria

- API 提供可測的 ingest、trace query、trace detail、timeline、state diff、claim/evidence flow、replay、research、admin surfaces
- API 回應能呈現 evidence grades、claim verification status、audit / policy / retention metadata
- web 具備 timeline、trace detail、replay、research、admin 頁面與共享 operator components
- edge daemon 具備 config、policy、spool、otlp、blob、health 模組與可編譯 skeleton
- Drive / arXiv connector 保留 source id、source uri、retrieved_at、query 與 provenance metadata
- e2e tests 覆蓋 ingest -> query -> replay 與 connector/admin contract
- deployment manifests 能描述 api / web / edge / postgres / redis / object-store baseline
- docs、plan、validation report 與實際檔案一致

## 5. Milestones

### Milestone 0 - Plan, fixture, and shared contracts
Goal
- 建立 3–10 的執行邊界，並先收斂共享 fixture 與 view-model 契約

Deliverables
- 本 plan
- richer trace bundle fixture
- shared API / UI models

Validation method
- 檢查 plan sections 完整
- compileall / inline JSON contract checks

Rollback / containment
- planning 與 shared model 變更不碰 live infra

### Milestone 1 - FastAPI ingest/query/replay plus governance
Goal
- 讓 API 成為 operator flow 的主資料入口

Deliverables
- API routers and services
- fixture-backed repository
- audit / policy / retention endpoints
- API tests

Validation method
- unit/integration/e2e tests
- compileall

Rollback / containment
- 全部為新增模組，可回退到 bootstrap `main.py`

### Milestone 2 - Edge daemon and connectors
Goal
- 建立 edge-side ingestion / spool / policy 邊界與 research connector skeleton

Deliverables
- Rust daemon crate
- Drive / arXiv connector modules
- worker entrypoints

Validation method
- `cargo check`
- compileall
- fixture contract tests

Rollback / containment
- 與 web/api 的 coupling 僅透過 typed payloads

### Milestone 3 - Operator web slices
Goal
- 建立能看 timeline、trace detail、state diff、claim/evidence flow 的 web shell

Deliverables
- timeline / traces / replay / research / admin pages
- reusable components
- local mock data adapter

Validation method
- TypeScript static inspection
- route/file existence checks

Rollback / containment
- UI 以 fixture data 驅動，不依賴 live backend

### Milestone 4 - E2E, deployment, docs, validation
Goal
- 補齊交付與 handoff 所需的測試、infra manifests、文件與驗證證據

Deliverables
- e2e tests
- Docker / Compose / K8s manifests
- docs and validation report

Validation method
- compileall
- cargo check
- inline manifest assertions

Rollback / containment
- infra 與 docs 變更可獨立 review，不影響 runtime code

## 6. Progress

- [x] 2026-04-17 12:04:00 UTC reread repo instructions, main guide, prior active plans, and task seeds for the 3–10 slice
- [x] 2026-04-17 12:04:00 UTC established this active ExecPlan and implementation boundary for API, edge, web, connectors, governance, e2e, and deployment
- [x] 2026-04-17 12:20:00 UTC Milestone 0 completed: shared fixture bundle, research fixtures, fixture loader, and operator-facing schema surface models landed
- [x] 2026-04-17 12:27:00 UTC Milestone 1 completed: FastAPI ingest/query/replay/research/admin routers, fixture-backed repository, and governance services landed
- [x] 2026-04-17 12:31:00 UTC Milestone 2 completed: worker entrypoints and `edge/daemon` Rust skeleton landed, and `cargo check --manifest-path edge/daemon/Cargo.toml` passed
- [x] 2026-04-17 12:39:00 UTC Milestone 3 completed: timeline, trace detail, replay, research, and admin Next.js routes plus shared components landed
- [-] 2026-04-17 12:47:00 UTC Milestone 4 partially completed: e2e tests, deployment manifests, docs, and validation report landed; `python -m compileall apps packages workers tests`, `cargo check`, and path assertions passed, but `uv` / `npm` backed validation remains blocked

## 7. Research notes

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` sections 10–13, 18–21
  Finding: timeline, state diff, evidence graph, why panel, replay hooks, Drive / arXiv provenance, governance, and deployment hardening are all part of the intended slice progression after canonical schema.
  Why it matters: this plan groups items 3–10 into the next executable vertical slice rather than separate disconnected stubs.
  Confidence: high

- Source: `docs/TASK_SEEDS.md` seeds 5–9
  Finding: ingestion API, connectors, operator UI shell, and why engine are expected to land as staged deliverables with tests and validation.
  Why it matters: the plan should keep those slices explicit and testable.
  Confidence: high

## 8. Surprises & Discoveries

- Current `tests/fixtures/canonical_trace_fixture.json` is too small for timeline/state diff/claim flow UI work, so a richer bundle fixture is required before implementing multiple surfaces.
- The environment still blocks package installation for Python and Node, so verification must rely on zero-download checks wherever possible.
- Keeping the Rust daemon dependency-free allowed `cargo check` to pass immediately without waiting for any external registry access.
- Using `packages/testkit/fixtures/` as the shared source of truth avoided a second mock-data contract drift between API, workers, and web.

## 9. Decision log

- 2026-04-17: implement items 3–10 as a fixture-backed vertical slice instead of waiting for live Postgres and live connectors.
  Rationale: it enables API/web/worker/edge contracts to converge now and leaves infra credentials as a follow-up concern.
  Alternatives rejected: postponing all work until live infra exists; this would stall the repository despite clear schema and product contracts.

- 2026-04-17: keep governance surfaces inside the API milestone rather than as a later bolt-on.
  Rationale: audit / policy / retention metadata affects ingestion and replay contracts from day one.
  Alternatives rejected: adding governance only after connectors/UI; that would force response-shape churn.

- 2026-04-17: keep the first edge daemon crate dependency-free.
  Rationale: the current environment can compile standard-library Rust immediately, which gives a trustworthy structural gate for the daemon boundary.
  Alternatives rejected: adding Tokio / OTLP crates now; that would reintroduce network-dependent validation risk in this environment.

## 10. Validation plan

- `python -m compileall apps packages workers tests`
- `python -m compileall edge`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `uv run pytest tests/unit -q`
- `uv run pytest tests/integration -q`
- `uv run pytest tests/e2e -q`
- inline Python contract checks for fixtures, deployment manifests, and route files
- if Node becomes available later:
  `npm run lint --workspace @aeris/web`
  `npm run typecheck --workspace @aeris/web`

## 11. Risks / Blockers

- Python dev dependencies are not currently installable because `uv sync --group dev` fails with PyPI DNS resolution errors.
- Node workspace commands are blocked by the current shell / launcher environment, so Next.js lint/typecheck cannot be executed here.
- Any live Google Drive or arXiv integration remains mock / fixture-only until credentials and networking policy are explicitly wired.

## 12. Deliverables

- `plans/active/20260417-platform-slices-3-10.md`
- API routers / services / repositories / governance modules
- richer fixture data
- web pages and components
- `edge/daemon/` crate
- worker entrypoints for ingest / replay / drive / arxiv
- e2e tests
- `infra/docker/*`
- `infra/compose/*`
- `infra/k8s/*`
- docs and validation report

## 13. Completion note

Platform slices 3 through 10 shipped as a fixture-backed skeleton.

Shipped
- FastAPI ingest/query/replay/research/admin route groups
- shared operator surface models and reusable fixtures
- Rust edge daemon crate with config/policy/spool/blob/otlp/health modules
- Next.js timeline, trace detail, replay, research, and admin pages
- worker entrypoints, e2e test files, and Docker / Compose / Kubernetes manifests
- architecture note and validation report

Did not ship
- live Postgres persistence
- live Google Drive or arXiv credentials
- dependency-backed pytest, mypy, ruff, eslint, or TypeScript execution

Follow-up
- replace fixture store with repository implementations over Postgres and blob storage
- wire live connector auth and rate-limit-safe fetch paths
- rerun the full repo validation gates once `uv` and `npm` installs work

Validation evidence lives in `reports/validation/20260417-platform-slices-3-10.md`.
