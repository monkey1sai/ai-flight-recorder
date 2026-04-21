# Canonical Schema Postgres Migrations

## 1. Purpose / Big Picture

為 AERIS Flight Recorder 建立第一版 Postgres canonical schema migrations，讓 repo 從 skeleton 進到真正可持久化的資料邊界。這一版重點是把 guide 與 `總覽.md` 定義的核心實體落成可審計、append-only、typed 的關聯表與 SQL migration 檔，供後續 ingestion API、timeline、state diff、why engine 與 connectors 直接依賴。

## 2. Scope

In scope
- 建立新的 active ExecPlan 並依進度更新
- 建立 canonical schema 的 Postgres migration SQL
- 補齊 `packages/schema` 的第一版 Python typed models
- 新增 migration fixtures、測試與 migration architecture doc
- 新增 major-work validation report

Out of scope
- Alembic / dbmate / Flyway 等 migration runtime 整合
- 真實 DB 啟動、`psql` 套用、或 Docker Compose
- spans / tasks / plan_versions / state_snapshots / counterfactual_runs / connectors tables
- ingest/query repository implementation

Assumptions
- 目前 repo 還沒有既定 migration toolchain，因此先用可 review 的 raw SQL migration 做最小 durable convention
- 這一輪只做主指南與 `docs/TASK_SEEDS.md` seed 4 指向的核心 observability entities
- UUID 會由 application 層或 Postgres `gen_random_uuid()` 任一方產生，因此 migration 先開 `pgcrypto`

Constraints
- 保持 append-only 思維，不設計會鼓勵 in-place mutation 的機制
- raw payload 與 normalized metadata 分離；DB 只存 `storage_ref` / `content_ref`
- 不修改 `.agents/skills/` 或 `.codex/`
- 驗證若受環境依賴阻塞，必須留下可重現 blocker 與靜態檢查證據

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `docs/TASK_SEEDS.md`
- `總覽.md`
- `plans/active/20260417-bootstrap-monorepo.md`

## 3. Repository context

Relevant files and directories
- `packages/schema/flight_recorder_schema/`
- `packages/schema/migrations/`
- `tests/unit/`
- `tests/integration/`
- `tests/smoke/`
- `docs/architecture/`
- `reports/validation/`

Current repo state
- bootstrap skeleton already exists, but no migration directory or DB schema
- `packages/schema` 只有 bootstrap-level `EvidenceGrade`, `HealthStatus`, `StepEnvelope`
- no Postgres-specific SQL or migration manifest exists yet

Planned touch surface
- `packages/schema/flight_recorder_schema/*`
- `packages/schema/migrations/*`
- `tests/*`
- `tests/fixtures/*`
- `docs/architecture/canonical-schema.md`
- `README.md`
- `reports/validation/20260417-canonical-schema-migrations.md`

## 4. Success criteria

- canonical migration SQL creates the core tables for `Session`, `Trace`, `Step`, `Observation`, `StateDelta`, `Artifact`, `EvidenceEdge`, `Claim`, `ExplanationRecord`, `Evaluation`, `Intervention`
- SQL clearly encodes append-only intent, foreign keys, JSONB metadata boundaries, and evidence-grade semantics
- a matching down migration exists
- Python typed models reflect the same entities and evidence-grade rules
- fixtures and tests cover migration/table presence plus model contracts
- docs explain where migrations live and how to apply them manually
- validation report records what was checked and what is still blocked

## 5. Milestones

### Milestone 0 - Schema boundary and plan
Goal
- translate guide/spec language into an executable schema/migration plan

Deliverables
- this ExecPlan
- scope and table boundary decisions

Validation method
- ensure the plan is self-sufficient under `.agent/PLANS.md`

Rollback / containment
- planning only; no runtime risk

### Milestone 1 - Canonical migration SQL
Goal
- create the first up/down migrations for the canonical observability entities

Deliverables
- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`

Validation method
- static checks against required tables, enums, indexes, and drop order

Rollback / containment
- migration is isolated to new SQL files

### Milestone 2 - Typed schema models and fixtures
Goal
- align Python schema package with the SQL contract

Deliverables
- typed entity models
- fixture JSON
- unit/integration/smoke tests

Validation method
- tests and syntax compilation

Rollback / containment
- changes confined to schema package and tests

### Milestone 3 - Docs and validation evidence
Goal
- make the migration convention handoff-ready for future milestones

Deliverables
- architecture note
- README update
- validation report

Validation method
- docs reference the actual paths and commands

Rollback / containment
- doc-only changes are independently reviewable

## 6. Progress

- [x] 2026-04-17 11:31:52 UTC reread `總覽.md`, `AGENTS.md`, `.agent/PLANS.md`, `docs/TASK_SEEDS.md`, main guide, and current bootstrap plan
- [x] 2026-04-17 11:31:52 UTC established the canonical migration scope and confirmed that migrations are the next repo priority after bootstrap
- [x] 2026-04-17 11:34:51 UTC Milestone 1 completed: first Postgres up/down migrations created under `packages/schema/migrations/`
- [x] 2026-04-17 11:34:51 UTC Milestone 2 completed: typed models, fixtures, and schema-focused tests added
- [-] 2026-04-17 11:34:51 UTC Milestone 3 partially completed: docs and validation report added; static checks passed, but dependency-backed pytest/lint/typecheck execution remains blocked by environment issues

## 7. Research notes

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 9
  Finding: canonical entities are `Session`, `Trace`, `Step`, `Observation`, `StateDelta`, `Artifact`, `EvidenceEdge`, `OutputClaim`, `ExplanationRecord`, `Evaluation`, `Intervention`.
  Why it matters: this is the exact minimum table set for the first migration.
  Confidence: high

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 9.2
  Finding: raw payload and normalized metadata must be separated; large content belongs in object storage; evidence graph should start as a relation table.
  Why it matters: migrations should store `storage_ref`/`content_ref` and JSONB metadata, not inline large payloads or graph-specific storage.
  Confidence: high

- Source: `總覽.md` tables overview
  Finding: Postgres is the canonical metadata store, and the first implementation sequence explicitly includes building Postgres migrations before the full API/UI.
  Why it matters: raw SQL migration files are a correct near-term deliverable even before repository integration layers exist.
  Confidence: high

- Source: `docs/TASK_SEEDS.md`
  Finding: the canonical schema seed expects migrations, model tests, and sample fixtures.
  Why it matters: this task should not stop at SQL alone.
  Confidence: high

## 8. Surprises & Discoveries

- The guide mixes two similar schemas: one conceptual entity list and one broader operational table catalog including `spans`, `tasks`, and `plan_versions`.
- To keep the migration focused, this task intentionally implements the seed-4 entity set and leaves the broader operational tables for follow-up migrations.
- The environment blockers from bootstrap still apply: PyPI DNS access fails and Node commands are unstable inside the current shell, so static validation remains the only reliable evidence path today.
- `python -m compileall apps packages workers tests` remained reliable after adding the new schema models and tests, so it is currently the best executable syntax gate available in this environment.

## 9. Decision log

- 2026-04-17: use raw SQL migrations under `packages/schema/migrations/` as the first durable convention.
  Rationale: the repo has no installed migration framework yet, and raw SQL is reviewable, tool-agnostic, and executable by `psql`.
  Alternatives rejected: introducing Alembic immediately; it would add dependency/runtime integration that the current environment cannot validate.

- 2026-04-17: keep `EvidenceEdge` polymorphic with `from_kind` / `to_kind` plus UUID endpoints, without foreign keys to every target entity.
  Rationale: relation-table graph edges span multiple entity kinds and the guide explicitly prefers a relation table before a graph DB.
  Alternatives rejected: per-entity join tables or graph-specific storage.

- 2026-04-17: use `storage_ref` / `content_ref` columns instead of inline raw payloads or a new blob table in this migration.
  Rationale: it preserves the raw-vs-normalized boundary without forcing object-store metadata design into the first migration.
  Alternatives rejected: introducing a `blobs` table now; that would broaden the scope beyond the requested canonical entities.

## 10. Validation plan

- `python -m compileall apps packages workers tests`
- `uv run pytest tests/unit -q`
- `uv run pytest tests/integration -q`
- `uv run pytest tests/smoke -q`
- inline Python checks for migration file presence and required SQL tokens
- optional future DB smoke once Postgres is available:
  `psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.up.sql`
  `psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.down.sql`

## 11. Risks / Blockers

- No live Postgres instance is available in this task, so migration execution is not verified against a real server.
- Python/Node dependency installation is still blocked in this environment, so pytest and lint/typecheck commands cannot be executed yet.
- Future migrations will need to reconcile this canonical entity set with broader operational tables such as `spans`, `tasks`, and `plan_versions`.

## 12. Deliverables

- `plans/active/20260417-canonical-schema-migrations.md`
- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`
- `packages/schema/flight_recorder_schema/canonical.py`
- updated `packages/schema/flight_recorder_schema/__init__.py`
- tests and fixture files for the canonical schema
- `docs/architecture/canonical-schema.md`
- `reports/validation/20260417-canonical-schema-migrations.md`

## 13. Completion note

Canonical schema migrations shipped at the file-contract level.

Shipped
- first Postgres up/down migration pair
- aligned Python typed models for the canonical entities
- fixture/test/docs coverage for the migration contract

Did not ship
- migration framework runtime integration
- live Postgres execution evidence
- dependency-backed pytest/lint/typecheck execution

Follow-up
- run the migration against a local Postgres instance once infrastructure is available
- add follow-up migrations for `spans`, `tasks`, `plan_versions`, and research-ingestion tables
- wire the ingest API and repositories to these tables

Validation evidence lives in `reports/validation/20260417-canonical-schema-migrations.md`.
