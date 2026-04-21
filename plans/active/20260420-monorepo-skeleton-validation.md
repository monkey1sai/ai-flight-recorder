# PR-001 Monorepo Skeleton Validation

## 1. Purpose / Big Picture

準備一個專注於 monorepo skeleton 可驗證性的 PR，讓 AERIS repo 在不實作產品功能的前提下，能夠被安裝、匯入、跑基本 Python / Node / Rust / Docker 驗證。完成後，reviewer 應能用明確命令重現目前哪些骨架已可運作、哪些仍有缺口。

## 2. Scope

In scope
- 從 `origin/master` 既有追蹤參考建立 `codex/p1-monorepo-skeleton-validation`
- 檢查 `apps/`、`packages/`、`workers/`、`tests/`、`pyproject.toml`、`package.json`、`Makefile`、`edge/`、`infra/`
- 修補 Python import layout，確保：
  - `from apps.api.app.main import app`
  - `from packages.schema.flight_recorder_schema import ...`
  - `from packages.testkit import ...`
- 最小化 pytest 與 workspace 設定，只讓 skeleton 可驗證
- 執行指定驗證命令並記錄 pass / fail / blocked
- 產出 `reports/codex/monorepo-skeleton-validation.md`

Out of scope
- AERIS 產品功能
- Drive connector、arXiv connector、Why Engine、database migrations、UI feature 擴充
- merge branch

Assumptions
- 目前工作樹中的 skeleton 內容是本次 PR 的基礎候選，不需要從零重建
- 若遠端無法存取，允許以本地 `origin/master` 追蹤參考建立分支並在報告中揭露限制

Constraints
- 保持 diff 聚焦於 monorepo testability
- 不重寫既有架構，只補齊 package/import/test wiring

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `plans/active/20260417-bootstrap-monorepo.md`
- `docs/ACCEPTANCE_CHECKLIST.md`
- `docs/BRANCHING.md`

## 3. Repository context

Relevant files
- `pyproject.toml`
- `package.json`
- `Makefile`
- `apps/api/app/main.py`
- `packages/schema/flight_recorder_schema/*`
- `packages/testkit/*`
- `tests/unit/*`
- `tests/smoke/*`
- `edge/daemon/Cargo.toml`
- `infra/compose/docker-compose.yml`

Current repo state
- repo 已有 bootstrap skeleton，但多數檔案尚未提交在目前分支
- Python packages 採 namespace-like layout，需驗證 pytest / uv 是否能穩定解析 root imports
- Node / Rust / Docker skeleton 已存在，但尚未確認是否通過本次指定命令

## 4. Success criteria

- 三個指定 Python import 在 `uv run python` 與 pytest 情境下均可用
- `uv sync --group dev`、`uv run ruff check .`、`uv run python -m pytest tests/unit -q`、`uv run python -m pytest tests/smoke -q` 至少有明確結果
- 若 `npm run lint --if-present`、`npm run typecheck --if-present`、`cargo check --manifest-path edge/daemon/Cargo.toml`、`docker compose -f infra/compose/docker-compose.yml config` 失敗，原因需可重現且文件化
- 產出 monorepo validation report，列出修正項、通過指令、失敗指令、精確 follow-up

## 5. Milestones

### Milestone 0 - Boundary and branch setup
Goal
- 建立本次 PR 分支與執行邊界

Deliverables
- 本 plan
- 分支建立結果與 fetch 限制記錄

Validation method
- `git status --short --branch`

### Milestone 1 - Import and config repair
Goal
- 讓 Python package layout 可被 root-level imports 與 pytest 穩定使用

Deliverables
- 必要的 `__init__.py` / pytest config / minimal module exports
- 若有需要，更新 `.gitignore` 或 repo config 以避免暫存產物污染驗證

Validation method
- `uv run python -c "...imports..."`
- `uv run python -m pytest tests/unit -q`

### Milestone 2 - Cross-tool validation
Goal
- 依使用者指定清單執行 Python / Node / Rust / Docker 驗證

Deliverables
- 通過的命令與失敗原因
- 必要的最小修補

Validation method
- 使用者指定命令逐條執行

### Milestone 3 - Evidence and handoff
Goal
- 產出可 review 的報告與 commit

Deliverables
- `reports/codex/monorepo-skeleton-validation.md`
- plan 更新
- git commit

Validation method
- 報告內容與實際命令一致

## 6. Progress

- [x] 2026-04-20 07:12:00 UTC reviewed repo instructions, prior bootstrap plan, acceptance checklist, and branching rules
- [x] 2026-04-20 07:16:00 UTC created `codex/p1-monorepo-skeleton-validation` from local `origin/master` reference after remote fetch failed due to DNS / thread issues
- [x] 2026-04-20 07:33:00 UTC Milestone 1 completed by adding `tests/conftest.py` so `uv run pytest ...` can resolve `apps` and `packages` imports from repo root
- [x] 2026-04-20 07:39:00 UTC Milestone 2 completed: `uv sync`, `ruff`, requested unit/smoke tests, npm lint/typecheck, and `cargo check` passed; exact `docker compose` command failed because installed Docker CLI lacks Compose v2 subcommand
- [x] 2026-04-20 07:42:00 UTC Milestone 3 completed with updated plan and `reports/codex/monorepo-skeleton-validation.md`
- [x] 2026-04-21 05:38:39 UTC CI merge blocker follow-up completed: replaced the machine-specific Python typecheck path with repo-local `pyright`, added `pyrightconfig.json`, and revalidated Python / Node / Rust gates locally

## 7. Research notes

- Source: `docs/BRANCHING.md`
  Finding: Codex work should branch from latest `master` and keep one concern per branch.
  Why it matters: this PR must stay limited to skeleton validation.
  Confidence: high

## 8. Surprises & Discoveries

- Remote fetch to GitHub currently fails in this environment, so branch freshness against live `origin/master` cannot be revalidated.
- `uv run python -m pytest ...` passed before code changes, but plain `uv run pytest ...` failed with `ModuleNotFoundError` for `apps` / `packages`; adding a repo-root path bootstrap in `tests/conftest.py` fixed the collection path issue without changing product modules.
- The machine has Docker CLI and classic `docker-compose`, but does not provide the `docker compose` v2 subcommand required by the requested validation command.
- The vendored `mypy-1.19.1-py3-none-any.whl` is not upstream mypy; it installs a local `mypy_compat` shim that hardcodes user-specific Node and global `pyright` paths, which breaks GitHub Actions and any machine that does not mirror the author workstation.
- `pyright` can resolve both `.venv` dependencies and repo-root imports for this monorepo once it is run with a repo-root `pyrightconfig.json` that sets `venvPath`, `venv`, and an execution environment `extraPaths` entry for `"."`.
- Re-running `npm ci --workspaces --include-workspace-root` in this local shell hit Windows `spawn EPERM`; existing `npm install`, web lint, and web typecheck still pass, so this appears to be a host-process or filesystem-lock condition rather than a repo config regression.

## 9. Decision log

- 2026-04-20: 以本地 `origin/master` 追蹤參考建立分支，而非等待遠端恢復。
  Rationale: 任務目標是本地 skeleton validation，可先完成 repo 內可驗證工作並揭露限制。
  Alternatives rejected: 停工等待網路恢復；會讓本地可完成工作無法推進。

- 2026-04-20: 以 `tests/conftest.py` 注入 repo root 到 `sys.path`，而不是新增額外 pytest plugin 依賴。
  Rationale: 這是最小且可攜的修補，能同時支援 `uv run pytest` 與 `uv run python -m pytest`。
  Alternatives rejected: 新增 `pytest-pythonpath` 或只要求一律使用 `python -m pytest`；前者增加依賴，後者未真正修好 import layout。

- 2026-04-21: 改用 repo-local `pyright` 和 `pyrightconfig.json` 取代 `uv run mypy ...` 的 machine-specific shim。
  Rationale: GitHub Actions 失敗的根因是 vendored fake mypy wheel 依賴某台機器上的全域 `pyright`; 改成 versioned Node dependency + repo config 才能讓本地與 CI 都可重現。
  Alternatives rejected: 繼續硬補全域 `pyright` 安裝；下載真正 mypy wheel 取代 vendor shim；前者仍不可攜，後者會擴大 vendor / lock 變更且對這個 skeleton milestone 沒有額外價值。

## 10. Validation plan

- `uv sync --group dev`
- `uv run python -c "from apps.api.app.main import app; from packages.schema.flight_recorder_schema import HealthStatus; from packages.testkit import load_trace_bundle_fixture; print(app.title, HealthStatus.__name__, load_trace_bundle_fixture().__class__.__name__)"`
- `uv run ruff check .`
- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/smoke -q`
- `npm run lint --if-present`
- `npm run typecheck --if-present`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `docker compose -f infra/compose/docker-compose.yml config`

## 11. Risks / Blockers

- GitHub remote 無法連線，若要 push / 開 Draft PR 可能同樣受阻
- 若 Node / Docker / Rust 工具在機器上缺失，需明確標記為 blocked 而不是假裝通過
- GitHub-hosted workflow 尚未用這個修補重跑一次，因此 merge readiness 仍需一次實際 PR rerun 才能從 local evidence 提升到 remote verified

## 12. Deliverables

- `plans/active/20260420-monorepo-skeleton-validation.md`
- minimal code / config fixes required for importability and tests
- `reports/codex/monorepo-skeleton-validation.md`
- focused git commit on `codex/p1-monorepo-skeleton-validation`

## 13. Completion note

Shipped
- task-specific plan for PR-001
- pytest import bootstrap via `tests/conftest.py`
- validation evidence in `reports/codex/monorepo-skeleton-validation.md`

Did not ship
- any new product feature
- Docker Compose tooling changes on the host machine

Follow-up
- install Docker Compose v2 or adjust the validation environment so `docker compose ...` is available
- restore network access if the branch must be refreshed from live `origin/master` before push / PR creation
- rerun the PR checks after pushing the `pyright` fix to verify the `python` job turns green on GitHub-hosted Windows runners
