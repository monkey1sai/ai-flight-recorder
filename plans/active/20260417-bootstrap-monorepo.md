# Bootstrap Monorepo Skeleton

## 1. Purpose / Big Picture

建立此 repo 的第一個可執行 monorepo skeleton，讓後續 Codex / 人類可以在既定契約下擴充 web、api、workers、schema 與驗證流程，而不是持續只停留在規格文件層。這個 bootstrap 要先交付可讀的目錄骨架、最小可跑的 API stub、web shell、`Makefile` 任務入口、測試與 validation 證據。

## 2. Scope

In scope
- 建立 active ExecPlan 並依 milestone 更新
- 補齊 monorepo 目錄骨架：`apps/`、`workers/`、`packages/`、`tests/`
- 建立 root `Makefile`、`package.json`、`pyproject.toml`、`.gitignore`
- 建立最小 FastAPI health endpoint 與 schema package
- 建立最小 Next.js App Router shell
- 建立 unit / integration / smoke 測試骨架與 validation report
- 更新 README 使其反映目前 repo 已進入 bootstrap 後狀態

Out of scope
- 真實 ingestion pipeline
- PostgreSQL / Redis / object storage 啟動腳本
- Google Drive / arXiv connector 實作
- Why Engine、timeline UI、evidence graph 真實功能
- CI/CD 與 deployment 基礎設施

Assumptions
- 目前 repo 仍是 docs-first kit，尚未有既定 app code 可延續
- 使用者要的是「可演進的實作骨架」，不是一次灌完整產品
- 開發環境可使用 `python`、`uv`、`node`；`make` 在本機可能尚未安裝

Constraints
- 不修改 `.agents/skills/` 與 `.codex/` 既有 workflow infrastructure
- 只做最小有效骨架，不混入 ingestion / connector / infra 額外需求
- 驗證優先跑最小集合，無法執行的部分必須明列缺口

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `docs/TASK_SEEDS.md`
- `docs/ACCEPTANCE_CHECKLIST.md`

## 3. Repository context

Relevant files
- `AGENTS.md`
- `README.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `docs/TASK_SEEDS.md`
- `docs/ACCEPTANCE_CHECKLIST.md`

Current repo state
- 目前只有規格、任務 seed、validation 資料夾與空的 `plans/active/`
- `plans/active/` 尚無 active ExecPlan
- 尚無 `Makefile`、`apps/`、`workers/`、`packages/`、`tests/`

Planned touch surface
- root config and manifests
- `apps/web`
- `apps/api`
- `workers/*`
- `packages/schema`
- `packages/ui`
- `packages/testkit`
- `tests/*`
- `reports/validation/*`

## 4. Success criteria

- repo 具備主指南建議的基本目錄骨架
- `apps/api` 提供可測試的 `/healthz` endpoint
- `apps/web` 有可 typecheck / lint 的最小畫面
- root `Makefile` 提供 `setup/lint/typecheck/unit/integration/smoke/test/validate`
- Python tests 至少覆蓋 health endpoint、schema 與 skeleton contract
- README 說明目前 bootstrap 結果與任務入口
- validation report 記錄執行過的指令、結果與剩餘風險

## 5. Milestones

### Milestone 0 - Bootstrap plan and boundaries
Goal
- 釐清 bootstrap 邊界，建立 active plan

Deliverables
- 本 plan 檔案
- repo map / assumptions / risk notes

Validation method
- 重新檢查計畫是否符合 `.agent/PLANS.md`

Rollback / containment
- 僅新增 plan，無執行碼風險

### Milestone 1 - Monorepo skeleton and developer contract
Goal
- 補齊 root manifests、目錄骨架與統一任務入口

Deliverables
- `Makefile`
- `.gitignore`
- root `package.json`
- root `pyproject.toml`
- 主要目錄與 placeholder 說明

Validation method
- 讀檔檢查結構
- 執行對應 lint/typecheck/test 命令

Rollback / containment
- 變更侷限在新建骨架檔案，無資料層風險

### Milestone 2 - Minimal runnable slices
Goal
- 建立最小 web / api / schema 可驗證切片

Deliverables
- `apps/api` FastAPI stub
- `packages/schema` models
- `apps/web` Next.js shell
- Python tests

Validation method
- unit / integration / smoke tests
- web lint / typecheck

Rollback / containment
- 若 web / api 其中一方卡住，至少保留另一方與 Makefile 合約

### Milestone 3 - Docs and validation evidence
Goal
- 讓 repo 能被下一位執行者直接接手

Deliverables
- README 更新
- validation report
- plan 進度更新

Validation method
- 文件與實際指令一致

Rollback / containment
- 文件層修改可獨立 review

## 6. Progress

- [x] 2026-04-17 11:18:31 UTC reviewed `AGENTS.md`, main guide, `.agent/PLANS.md`, `docs/TASK_SEEDS.md`, `總覽.md`, README, acceptance checklist
- [x] 2026-04-17 11:18:31 UTC established repo map and bootstrap boundary
- [x] 2026-04-17 11:27:58 UTC Milestone 1 completed: root manifests, `Makefile`, `apps/`, `packages/`, `workers/`, `tests/` skeleton created
- [x] 2026-04-17 12:58:41 UTC Milestone 2 completed: offline Python wheelhouse, repo-local npm wrapper, FastAPI stub, schema package, Next.js shell, and validation commands all pass
- [x] 2026-04-17 12:58:41 UTC Milestone 3 completed with final evidence: README, plan, lockfiles, vendor artifacts, and non-partial validation report are aligned

## 7. Research notes

- Source: `AGENTS.md`
  Finding: repo contract requires `Makefile` targets and validation evidence before declaring meaningful work complete.
  Why it matters: bootstrap must include task entrypoints, not just folders.
  Confidence: high

- Source: `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
  Finding: recommended monorepo layout is `apps/`, `workers/`, `packages/`, with Next.js web and FastAPI API.
  Why it matters: skeleton should follow the canonical layout to reduce future churn.
  Confidence: high

- Source: `docs/TASK_SEEDS.md`
  Finding: seed task explicitly asks for first ExecPlan plus smallest usable monorepo skeleton, Makefile targets, lint/typecheck/test wiring, and validation report.
  Why it matters: this is the most direct operational interpretation of the user's request.
  Confidence: high

## 8. Surprises & Discoveries

- `plans/active/` 目前只有 `.gitkeep`，代表 bootstrap 前沒有任何 active implementation plan。
- 本機有 `python`、`node`、`uv`，但 `make` 不存在；因此需要同時提供 Makefile 契約與底層可直接執行命令。
- git repo 存在 safe.directory 警告，需用 `git -c safe.directory=...` 才能查看狀態。
- 這個 Windows shell 一開始缺少 `TEMP`、`TMP`、`SystemRoot`、`windir`、`ComSpec`，會同時破壞 `uv` 安裝流程、`node.exe` 啟動，以及 `asyncio.windows_events` 匯入。
- `uv` 離線解析可透過 repo-local wheelhouse 補齊；其中 `pydantic-core` 與自製 `mypy` shim wheel 必須明確 vendor，否則 `--offline` 仍會回退到 registry resolution。
- `npm` 不必改動系統安裝；以 `tools/bin/npm.cmd` / `tools/bin/npm.ps1` 包裝可穩定走 repo-local cache 與可用的 Node runtime。
- `uv run pytest` 在此 Windows 組合下會走到 entrypoint import path 問題；改成 `uv run python -m pytest` 可穩定保留 repo root import resolution。

## 9. Decision log

- 2026-04-17: 先做 docs-aligned skeleton，不直接展開 ingestion / connector 實作。
  Rationale: user request is bootstrap-oriented and seed tasks also define this as first milestone.
  Alternatives rejected: 直接生成完整產品 codebase；風險太大且超出最小安全變更面。

- 2026-04-17: 以最小可執行 stub 驗證 web/api/schema，而不是只做空目錄。
  Rationale: 可讓 lint/typecheck/test 立即有落點。
  Alternatives rejected: 僅建立空資料夾與 README；對後續開發幫助太小。

- 2026-04-17: 保留 FastAPI / Next.js manifests，即使本輪無法安裝依賴。
  Rationale: skeleton 的價值在於固定未來實作邊界與工具契約，而不是為了通過當前受限環境而退回無框架 placeholder。
  Alternatives rejected: 改成純標準函式庫或純靜態 HTML；會偏離主指南指定的技術方向。

- 2026-04-17: 以 repo-local vendor wheelhouse 與 npm wrapper 解決安裝問題，而非依賴全域環境修復。
  Rationale: 可在目前 shell 權限內重現，且不需要修改 `Program Files` 下的系統 wrapper。
  Alternatives rejected: 直接修改全域 `npm.cmd` / `npm.ps1`；此環境沒有寫入權限且會放大系統層風險。

- 2026-04-17: 將 pytest 驗證命令改為 `uv run python -m pytest ...`。
  Rationale: 這是目前可重現且不需要額外插件的做法，能避免 Windows entrypoint 導致的 namespace import 失敗。
  Alternatives rejected: 繼續使用 `uv run pytest ...`；在此環境下會穩定出現 `ModuleNotFoundError`。

## 10. Validation plan

- `uv sync --group dev --offline`
- `npm install --workspaces --include-workspace-root --offline`
- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/smoke -q`
- `uv run ruff check .`
- `uv run mypy apps packages workers tests`
- `npm run lint --workspace @aeris/web`
- `npm run typecheck --workspace @aeris/web`
- `python -m compileall apps packages workers tests`
- custom path / Makefile contract check via inline `python -`

## 11. Risks / Remaining Notes

- `make` 尚未安裝，因此本次驗證不能直接以 `make <target>` 執行，只能驗證 Makefile 所包裝的底層命令。
- bootstrap Python 與 npm 驗證目前依賴 repo-local vendor artifacts：`vendor/python/wheels/`、`vendor/npm/brace-expansion-1.1.14.tgz`、`tools/bin/npm.*`。
- web skeleton 採最小 Next.js shell；本 plan 的前端驗證仍限於 lint + typecheck，尚未納入 UI tests。

## 12. Deliverables

- `plans/active/20260417-bootstrap-monorepo.md`
- root manifests and ignore rules
- `apps/web/*`
- `apps/api/*`
- `workers/*`
- `packages/schema/*`
- `packages/ui/README.md`
- `packages/testkit/README.md`
- `tests/*`
- `reports/validation/20260417-bootstrap-monorepo.md`

## 13. Completion note

Bootstrap skeleton is now fully validated within the current repository boundary.

Shipped
- root manifests: `Makefile`, `package.json`, `pyproject.toml`, `.gitignore`
- minimal `apps/api`, `apps/web`, `packages/schema`, `workers/*`, `tests/*`
- offline Python wheelhouse, repo-local npm wrapper, `uv.lock`, `package-lock.json`, and vendored npm tarball for reproducible local setup
- README refresh, updated plan, and final validation report

Did not ship
- any real ingestion, storage, connector, or UI operator features
- UI automation / browser e2e coverage

Follow-up
- if future work changes Python or Node dependency versions, refresh the corresponding vendor artifacts and rerun the validation set from section 10
- after bootstrap, continue feature work from the newer milestone-specific plans in `plans/active/`

Validation evidence lives in `reports/validation/20260417-bootstrap-monorepo.md`.
