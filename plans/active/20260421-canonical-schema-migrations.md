# Canonical Schema Postgres Migrations

## 1. Purpose / Big Picture

為 AERIS Flight Recorder 建立第一版 Postgres canonical schema migration，讓 repo 從規格與 README 宣告進到可 review、可驗證的資料邊界。這一輪只交付 migration slice 本身：SQL、typed models、migration tests、架構說明與驗證證據。

## 2. Scope

In scope
- 建立 canonical schema 的 first migration SQL
- 建立最小 Python schema package 以反映 migration entity contract
- 新增 migration-focused unit / integration tests
- 新增 architecture note、validation report、codex report
- 更新此 active ExecPlan

Out of scope
- migration runtime integration
- live Postgres 啟動與 `psql` smoke
- ingest/query repository implementation
- web / api / workers skeleton

Assumptions
- 目前 `master` 還沒有 schema package 與 migration files
- 這個 task 只需要 seed-4 觀測實體，不需要 broader operational tables

Constraints
- 保持單一小 PR
- 不引入與 migration 無關的 bootstrap 或 UI/API 結構
- 只建立跑 targeted `ruff` / `pytest` 所需的最小 Python project 設定

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `docs/architecture/canonical-schema.md`

## 3. Repository context

Relevant files
- `pyproject.toml`
- `packages/schema/flight_recorder_schema/*`
- `packages/schema/migrations/*`
- `tests/unit/*`
- `tests/integration/*`
- `docs/architecture/*`
- `reports/validation/*`
- `reports/codex/*`

Current repo state
- `master` 缺少 `packages/schema/` 與 migration files
- README 已宣告 canonical migration，但檔案尚未在此 branch 落地

## 4. Success criteria

- 有 `0001_canonical_schema.up.sql` / `down.sql`
- migration 涵蓋 `sessions`, `traces`, `steps`, `observations`, `state_deltas`, `artifacts`, `evidence_edges`, `claims`, `explanation_records`, `evaluations`, `interventions`
- Python typed models 反映 migration 中的 enums 與 record contracts
- targeted tests 能檢查 SQL tokens 與 canonical models
- 有 architecture note、validation report、codex report

## 5. Milestones

### Milestone 0 - Plan and boundaries
Goal
- 建立 migration 小 PR 的邊界與 deliverables

Deliverables
- 本 plan

Validation method
- plan 結構符合 `.agent/PLANS.md`

### Milestone 1 - SQL and typed models
Goal
- 建立 canonical migration SQL 與最小 schema models

Deliverables
- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`
- `packages/schema/flight_recorder_schema/*`

Validation method
- targeted pytest
- static import checks

### Milestone 2 - Docs and evidence
Goal
- 補齊 migration note、validation report、codex report

Deliverables
- `docs/architecture/canonical-schema.md`
- `reports/validation/20260421-canonical-schema-migrations.md`
- `reports/codex/postgres-migrations.md`

Validation method
- links and paths resolve

## 6. Progress

- [x] 2026-04-21 06:05:00 UTC reviewed `AGENTS.md`, main guide, `.agent/PLANS.md`, and the existing migration plan from the other active branch to extract the smallest migration-only slice
- [x] 2026-04-21 06:10:00 UTC created isolated branch `codex/postgres-migrations` from `master` in a separate worktree to avoid unrelated staged and untracked changes
- [x] 2026-04-21 06:24:00 UTC Milestone 1 completed: added first canonical Postgres up/down migrations plus the minimal typed schema package
- [x] 2026-04-21 06:28:00 UTC Milestone 2 completed: added migration-focused tests, architecture note, validation report, and codex evidence report

## 7. Research notes

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 9
  Finding: canonical entities include Session, Trace, Step, Observation, StateDelta, Artifact, EvidenceEdge, OutputClaim, ExplanationRecord, Evaluation, Intervention.
  Why it matters: defines the minimal migration table set.
  Confidence: high

## 8. Surprises & Discoveries

- `master` currently has no `packages/schema/` tree even though README already references canonical migrations.
- `uv sync --group dev` partially created `.venv` but failed to persist one wheel metadata file with Windows access-denied errors; `uv run ...` still worked for `ruff` and targeted pytest in this worktree.
- `pytest` collection from `uv run pytest ...` did not resolve the repo root import path by default, so a minimal `tests/conftest.py` path bootstrap was needed even for this migration-only slice.
- Both `ruff` and `pytest` emitted cache-directory access warnings in this worktree; the checks still completed successfully, so these warnings were treated as host-environment noise rather than product failures.

## 9. Decision log

- 2026-04-21: isolate this work in a fresh worktree and branch from `master`.
  Rationale: current working branch contains unrelated staged/untracked changes and would break the “one small PR” requirement.
  Alternatives rejected: implementing directly on the existing dirty branch.

- 2026-04-21: keep the migration PR limited to `packages/schema`, targeted tests, and migration evidence instead of importing the full monorepo bootstrap.
  Rationale: the user asked for one small PR specifically for Postgres migrations; pulling in web/api/workers would violate scope.
  Alternatives rejected: cherry-picking the larger bootstrap branch wholesale.

## 10. Validation plan

- `uv run ruff check .`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/unit/test_canonical_models_contract.py -q -p no:cacheprovider`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/integration/test_canonical_migration_spec.py -q -p no:cacheprovider`

## 11. Risks / Blockers

- No live Postgres instance is available for migration execution smoke.
- `uv sync --group dev` still hits a Windows filesystem permission issue in this worktree, so reproducibility is currently verified through successful `uv run` commands rather than a clean sync pass.

## 12. Deliverables

- `pyproject.toml`
- `packages/schema/flight_recorder_schema/__init__.py`
- `packages/schema/flight_recorder_schema/canonical.py`
- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`
- `tests/conftest.py`
- `tests/unit/test_canonical_models_contract.py`
- `tests/integration/test_canonical_migration_spec.py`
- `docs/architecture/canonical-schema.md`
- `reports/validation/20260421-canonical-schema-migrations.md`
- `reports/codex/postgres-migrations.md`

## 13. Completion note

Shipped
- first canonical Postgres up/down migration pair
- minimal typed schema models aligned to the SQL contract
- targeted unit/integration tests for model and migration token coverage
- architecture note, validation report, and codex PR evidence

Did not ship
- live Postgres execution
- migration runtime integration
- broader operational tables like `spans`, `tasks`, or `plan_versions`

Follow-up
- run the migration on a real Postgres instance
- add subsequent migrations for broader operational tables
- replace the temporary path bootstrap in `tests/conftest.py` if a future repo-wide pytest strategy is introduced

Validation evidence lives in `reports/validation/20260421-canonical-schema-migrations.md`.
