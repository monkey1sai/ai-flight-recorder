# Bootstrap Governance Baseline

## 1. Purpose / Big Picture

建立這個 repo 的開發治理基線，讓 Codex 與人類之後能用小 PR 安全演進，而不是在未定義 review、CI、忽略規則、完成標準與本地驗證入口的情況下直接疊功能。這一輪不做新產品功能，只處理 repo 命名一致化、治理、CI、文件與驗證腳本。

## 2. Scope

In scope
- 稽核目前 repo 結構與未提交變更
- 確認 `node_modules`、`.venv`、cache、generated files、secrets 是否被意外追蹤
- 補強 `.gitignore`
- 新增 GitHub governance artifacts：
  - `.github/workflows/ci.yml`
  - `.github/workflows/codex-review.yml`
  - `.github/codex/prompts/review.md`
  - `.github/pull_request_template.md`
  - `CODEOWNERS`
- 新增治理文件：
  - `docs/DEVELOPMENT_WORKFLOW.md`
  - `docs/BRANCHING.md`
  - `docs/DEFINITION_OF_DONE.md`
- 新增本地驗證腳本：
  - `scripts/verify-local.ps1`
  - `scripts/verify-local.sh`
- 執行可用驗證並記錄結果
- 撰寫 `reports/codex/bootstrap-governance-audit.md`
- 將 repo / 專案識別名對齊 `總覽.md` 的 AERIS 命名

Out of scope
- 新產品功能
- API / UI / connector / persistence 實作
- 刪除既有使用者工作
- 重構產品程式碼
- 推送、合併、改寫 git history

Assumptions
- 目前大量檔案仍是未提交狀態，這次只能在既有工作樹上疊加治理檔案
- 使用者要求的「更改名稱」是調整 repo / 專案識別與 metadata，不是直接重命名目前工作目錄路徑
- GitHub Actions 以 Linux runner 為主，需兼顧 Node / Python / Rust / Docker Compose 基本驗證

Constraints
- 不覆蓋既有未提交 product work
- 改動只限 governance / CI / docs / validation scripts / metadata naming
- 若現有命令失敗，需保留失敗原因與可能成因到報告

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `README.md`
- `package.json`
- `pyproject.toml`
- `Makefile`
- `總覽.md`

## 3. Repository context

Relevant files and directories
- `.gitignore`
- `.github/` (currently missing)
- `docs/`
- `scripts/`
- `reports/`
- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `uv.lock`
- `Makefile`

Current repo state
- 目前只有少量歷史追蹤檔，絕大多數 monorepo skeleton 仍為未追蹤狀態
- `.gitignore` 只涵蓋部分 Python / Node 暫存，未涵蓋 Rust `target/`、更多 cache、env / secrets、OS / editor 雜訊
- `.github/` 目錄尚不存在
- `README.md` 已使用 `AERIS Flight Recorder`，但 `package.json`、`pyproject.toml`、`package-lock.json`、`uv.lock` 仍使用 `aeris-flight-recorder`
- `.venv/`、`node_modules/`、`.pytest_cache/`、`.ruff_cache/`、`.uv-cache/`、`edge/daemon/target/` 都存在於工作樹

Planned touch surface
- `.gitignore`
- `.github/**`
- `CODEOWNERS`
- `docs/**`
- `scripts/verify-local.ps1`
- `scripts/verify-local.sh`
- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `uv.lock`
- `README.md` (only if required for naming consistency)
- `reports/codex/bootstrap-governance-audit.md`

## 4. Success criteria

- repo 有可審查的治理基線文件與 CI workflows
- `.gitignore` 可明確忽略常見 generated / cache / local-secret 類型檔案
- 稽核結果清楚說明哪些 generated / secret-like 檔案存在、哪些已被追蹤、哪些未被追蹤
- CI workflow 至少定義 Node、Python、Rust、docker compose config validation 路徑
- Codex review workflow 以 read-only advisory mode 運作
- PR template、CODEOWNERS、development docs 可支援小 PR 開發節奏
- 本地驗證腳本可統一呼叫既有 repo contract
- 報告記錄成功與失敗驗證、未解 blocker、命名調整、以及剩餘風險

## 5. Milestones

### Milestone 0 - Audit and planning
Goal
- 完成 repo 結構、git 狀態、忽略規則缺口、命名落差與治理邊界盤點

Deliverables
- 本 plan
- 稽核筆記與風險清單

Validation method
- 檢查 plan 與稽核輸入來源完整

Rollback / containment
- 僅新增 plan 與分析，不動產品碼

### Milestone 1 - Repo hygiene and naming baseline
Goal
- 補齊 `.gitignore` 並將 repo 識別名對齊 AERIS

Deliverables
- 更新 `.gitignore`
- 必要 metadata 命名更新

Validation method
- `git status --short`
- `git ls-files` 檢查生成物是否被追蹤

Rollback / containment
- 僅 metadata / ignore 改動，與產品功能隔離

### Milestone 2 - GitHub governance and docs
Goal
- 建立 review / CI / PR / ownership / development process 基線

Deliverables
- workflows
- review prompt
- CODEOWNERS
- PR template
- development workflow docs

Validation method
- YAML / path existence checks
- 文件內容人工校對

Rollback / containment
- 全為治理檔案，可獨立審查

### Milestone 3 - Local verification and reporting
Goal
- 提供本地驗證入口並寫出治理稽核報告

Deliverables
- `scripts/verify-local.ps1`
- `scripts/verify-local.sh`
- `reports/codex/bootstrap-governance-audit.md`

Validation method
- 執行可用命令
- 將失敗與原因寫入報告

Rollback / containment
- 不更動產品碼，只增加驗證包裝與報告

## 6. Progress

- [x] 2026-04-20 05:36 UTC reread `AGENTS.md`, `.agent/PLANS.md`, main guide, `README.md`, manifests, `Makefile`, current git status, and tracked diff
- [x] 2026-04-20 05:36 UTC audited current working tree shape, ignore gaps, tracked files, and name mismatches versus `總覽.md`
- [x] 2026-04-20 05:52 UTC completed Milestone 1 by aligning root metadata naming to `aeris` and expanding `.gitignore` to cover generated directories, toolchain homes, and local machine config
- [x] 2026-04-20 06:03 UTC completed Milestone 2 by adding CI, Codex advisory review workflow, review prompt, PR template, CODEOWNERS, and governance docs
- [x] 2026-04-20 06:18 UTC completed Milestone 3 by adding local verification scripts, running available checks, and writing `reports/codex/bootstrap-governance-audit.md`

## 7. Research notes

- Source: `總覽.md`
  Finding: the recommended formal product name is `AERIS Flight Recorder`, with AERIS as the umbrella identity.
  Why it matters: repo / project metadata should align to the documented naming baseline.
  Confidence: high

- Source: current git status / `git ls-files`
  Finding: monorepo skeleton files are currently untracked, while cache directories like `node_modules/` and `.venv/` are present locally but not tracked.
  Why it matters: governance work must avoid accidentally staging generated directories and should strengthen ignore rules before future PRs.
  Confidence: high

## 8. Surprises & Discoveries

- The repository still has a very small tracked baseline; most implementation files are untracked rather than already versioned.
- `.codex/config.toml` exists locally but is not tracked; `.codex/.codex-log/` exists and should remain ignored.
- Access-denied errors occur when recursively scanning some cache directories from PowerShell, so audit commands must avoid traversing known generated paths directly.
- `.npmrc` is present as local machine configuration with cache preferences, so it should not be committed as project governance.
- `總覽.md` was already aligned to `AERIS Flight Recorder`; the rename gap was in root package metadata, not in the architecture overview document itself.
- Local `uv` commands require `UV_CACHE_DIR` pointed inside the workspace to avoid sandbox access-denied failures.
- `pytest tests/smoke` passes when `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `-p no:cacheprovider` are used, but unit / integration / e2e collection still fail inside the sandboxed Windows Python runtime.
- Local Docker only exposes `docker-compose`, while GitHub-hosted CI is expected to support `docker compose`.
- Repo-local npm wrappers work when invoked directly, so the PowerShell verification script was updated to prefer `tools/bin/npm.ps1`.
- Rust validation can avoid home-directory permission errors with repo-local `CARGO_HOME` / `RUSTUP_HOME`, but still needs a configured default toolchain to pass.

## 9. Decision log

- 2026-04-20: interpret the rename request as repo/project identity alignment to AERIS, not a filesystem directory rename.
  Rationale: changing the live workspace path would be riskier and outside the requested governance-only scope.
  Alternatives rejected: renaming `C:\Repos\active\ai-agent\AI-Flight-Recorder` directly.

- 2026-04-20: keep governance changes isolated from product code and fixture behavior.
  Rationale: user explicitly asked not to implement new product features or refactor product code.
  Alternatives rejected: bundling persistence or API cleanup together with governance.

- 2026-04-20: add `issues: write` to the Codex advisory workflow permissions.
  Rationale: the workflow posts an issue-style PR comment via `github.rest.issues.createComment`, so `pull-requests: write` alone is not a safe minimum.
  Alternatives rejected: relying on implicit permissions or changing the workflow to mutate review state.

- 2026-04-20: prefer repo-local npm wrappers in local verification scripts.
  Rationale: sandboxed direct `npm` execution showed Node runtime / install-directory instability, while `tools/bin/npm.ps1` completed lint and typecheck successfully.
  Alternatives rejected: forcing system `npm` or embedding installation logic into governance scripts.

## 10. Validation plan

- `git -c safe.directory='C:/Repos/active/ai-agent/AI-Flight-Recorder' status --short`
- `git -c safe.directory='C:/Repos/active/ai-agent/AI-Flight-Recorder' ls-files`
- `uv run ruff check .`
- `uv run mypy apps packages workers tests`
- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/e2e -q`
- `uv run python -m pytest tests/smoke -q`
- `npm run lint --workspace @aeris/web`
- `npm run typecheck --workspace @aeris/web`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `docker compose -f infra/compose/docker-compose.yml config`

## 11. Risks / Blockers

- Existing untracked product skeleton means any broad git operation could accidentally pull in unrelated files.
- Local environment previously had `uv` / `npm` execution issues; validation may still partially fail.
- GitHub Actions can be authored, but not executed locally inside this task.

## 12. Deliverables

- `plans/active/20260420-bootstrap-governance-baseline.md`
- updated `.gitignore`
- `.github/workflows/ci.yml`
- `.github/workflows/codex-review.yml`
- `.github/codex/prompts/review.md`
- `CODEOWNERS`
- `.github/pull_request_template.md`
- `docs/DEVELOPMENT_WORKFLOW.md`
- `docs/BRANCHING.md`
- `docs/DEFINITION_OF_DONE.md`
- `scripts/verify-local.ps1`
- `scripts/verify-local.sh`
- `reports/codex/bootstrap-governance-audit.md`

## 13. Completion note

Completed on 2026-04-20. Governance baseline artifacts, naming alignment, local verification entrypoints, and the audit report were added without touching product behavior. Remaining gaps are documented in `reports/codex/bootstrap-governance-audit.md`, especially the sandboxed Windows Python runtime failures for non-smoke pytest suites and the missing default Rust toolchain for repo-local cargo validation.
