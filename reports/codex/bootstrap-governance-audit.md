# Bootstrap Governance Audit

Date: 2026-04-20
Repo: `C:\Repos\active\ai-agent\AI-Flight-Recorder`
Audit scope: governance baseline only

## 1. Executive summary

這一輪工作沒有新增產品功能，也沒有重構產品碼。範圍限制在 repo 命名對齊、忽略規則、GitHub workflows、PR/review 治理檔、開發流程文件、本地驗證腳本，以及對目前工作樹的稽核。

根據 `總覽.md`，正式產品名稱已經定義為 `AERIS Flight Recorder`。本次同步把 root metadata 對齊成 `AERIS` / `aeris`，但沒有重命名實體工作目錄 `C:\Repos\active\ai-agent\AI-Flight-Recorder`，因為那會超出治理基線與小變更邊界。

## 2. Repository audit

### 2.1 Git state

- `README.md` 是唯一已追蹤但未提交的修改檔。
- 目前 monorepo 骨架的大部分內容仍是未追蹤狀態，包含 `apps/`、`packages/`、`workers/`、`edge/`、`infra/`、`.github/` 等。
- 這代表本次治理變更無法假設 repo 已有穩定的已版本化基線；任何廣泛 `git add .` 都有把大量既有骨架一併納入的風險。

### 2.2 Generated files / caches / local state

本地存在以下 generated 或 local-only 目錄：

- `node_modules/`
- `.venv/`
- `.pytest_cache/`
- `.ruff_cache/`
- `.uv-cache/`
- `.cargo-home/`
- `.rustup-home/`

稽核結論：

- 這些目錄目前沒有被歷史追蹤。
- 原本 `.gitignore` 尚未完整涵蓋 `.cargo-home/`、`.rustup-home/`、`.npmrc` 等本地治理噪音；本次已補上。

### 2.3 Secret / machine-specific files

發現以下需特別注意的本地設定：

- `.npmrc`

內容屬於使用者本機 cache / offline 偏好設定，而非產品必要設定，因此視為 machine-specific local config。這次沒有讀取或修改敏感憑證內容，也沒有發現已追蹤的 `.env`、`auth.json`、`credentials.json`、證書私鑰等 secret-like 檔案。

稽核結論：

- 未發現已被 Git 追蹤的 secret-like 檔案。
- 為避免未來誤提交，本次已將 `.npmrc` 與常見 secret / cert 檔型納入 `.gitignore`。

## 3. Naming alignment

### 3.1 Source of truth

- `總覽.md`
- `README.md`

### 3.2 Applied changes

已將以下 root metadata 對齊為 `aeris`：

- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `uv.lock`

未進行的動作：

- 未重命名磁碟路徑
- 未改動產品 fixture 內容或工作區示例資料

理由：

- 使用者要求的目標是先建立可安全開發的治理基線。
- 直接重命名 workspace 路徑屬高風險操作，且會影響本地工具、Git safe.directory、可能的 IDE 設定與腳本路徑。

## 4. Governance files added

### 4.1 Ignore and hygiene

- `.gitignore`

### 4.2 GitHub governance

- `.github/workflows/ci.yml`
- `.github/workflows/codex-review.yml`
- `.github/codex/prompts/review.md`
- `CODEOWNERS`
- `.github/pull_request_template.md`

### 4.3 Process docs

- `docs/DEVELOPMENT_WORKFLOW.md`
- `docs/BRANCHING.md`
- `docs/DEFINITION_OF_DONE.md`

### 4.4 Local validation entrypoints

- `scripts/verify-local.ps1`
- `scripts/verify-local.sh`

## 5. Workflow review

### 5.1 CI workflow

`ci.yml` 目前覆蓋：

- repo hygiene
- Python validation
- Node validation
- Rust validation
- docker compose config validation

設計備註：

- Python job 使用 `windows-latest`，不是預設 Linux。原因是目前 `pyproject.toml` / `vendor/python/wheels` 內容明顯偏向 Windows wheel 基線，例如 `pydantic_core-...win_amd64.whl`、`ruff-...win_amd64.whl`。
- docker compose 檢查以 GitHub Actions 的 `docker compose` 為主；本地環境則另外在驗證腳本中兼容 `docker-compose`。

### 5.2 Codex advisory review workflow

`codex-review.yml` 目前特性：

- advisory only
- `sandbox: read-only`
- `safety-strategy: drop-sudo`
- 只在非 draft、且 PR head repo 與 base repo 相同時執行
- 透過 `.github/codex/prompts/review.md` 定義 review focus

補充修正：

- workflow permissions 已加上 `issues: write`，因為最後是用 issue comment 方式回貼 advisory review 結果。

## 6. Validation commands run

以下為本次實際執行紀錄與結果。

### 6.1 Repository / hygiene audit

Command:

```powershell
git -c safe.directory='C:/Repos/active/ai-agent/AI-Flight-Recorder' status --short
```

Result:

- 成功
- 顯示 `README.md` 為已追蹤修改，其餘大量 monorepo 骨架為未追蹤

Command:

```powershell
git -c safe.directory='C:/Repos/active/ai-agent/AI-Flight-Recorder' ls-files
```

Result:

- 成功
- 未發現 `node_modules`、`.venv`、`.pytest_cache`、`.ruff_cache`、`.uv-cache`、`target/` 等 generated 目錄已被追蹤

### 6.2 Python validation

Command:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache'); uv run ruff check .
```

Result:

- 成功
- `All checks passed!`

Command:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
uv sync --group dev
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache'); uv run python -m mypy apps packages workers tests
```

Result:

- 失敗
- `No module named mypy`

Likely cause:

- `uv sync --group dev` 本身可以完成，但之後 `uv run python -m mypy` 仍然找不到 module，表示目前 `.venv` / `uv run` 的解析狀態不一致。
- 直接呼叫 `.venv\Scripts\mypy.exe` 在 sandbox 內又觸發 launcher / runtime 異常，因此這不是單純少打一個 setup 指令就能穩定解決的狀況。

Command:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
uv run python -m pytest tests/smoke -q -p no:cacheprovider
```

Result:

- 成功
- `4 passed`

Command:

```powershell
$env:UV_CACHE_DIR = (Join-Path (Get-Location) '.uv-cache')
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
uv run python -m pytest tests/unit -q -p no:cacheprovider
uv run python -m pytest tests/integration -q -p no:cacheprovider
uv run python -m pytest tests/e2e -q -p no:cacheprovider
```

Result:

- 失敗
- collection/import 階段出現 Windows `asyncio` / `_overlapped` 相關錯誤，例如：
  - `OSError: [WinError 10106] 無法載入或初始化所要求的服務提供者`
  - `NameError: name 'base_events' is not defined`

Likely cause:

- 比較像是目前 sandbox / Python runtime 本身異常，而不是 repo 測試邏輯單純失敗。
- 問題發生於 stdlib `asyncio` 與 Windows provider 初始化，不像一般專案層級斷言失敗。

### 6.3 Node validation

Command:

```powershell
& '.\tools\bin\npm.ps1' run lint --workspace @aeris/web
& '.\tools\bin\npm.ps1' run typecheck --workspace @aeris/web
```

Result:

- 成功

Notes:

- 直接使用 repo-local PowerShell npm wrapper 可以通過。
- 原生 `npm` 在 sandbox 內有 Node install directory / crypto assertion 類異常，因此本次本地腳本已改成優先走 `tools/bin/npm.ps1`。

### 6.4 Rust validation

Command:

```powershell
$env:CARGO_HOME = (Join-Path (Get-Location) '.cargo-home')
$env:RUSTUP_HOME = (Join-Path (Get-Location) '.rustup-home')
cargo check --manifest-path edge/daemon/Cargo.toml
```

Result:

- 失敗
- `rustup could not choose a version of cargo to run ... no default is configured`

Likely cause:

- 使用 repo-local `CARGO_HOME` / `RUSTUP_HOME` 之後，避開了原本 sandbox 對使用者家目錄的存取限制，但本地 repo-local rustup home 尚未安裝或設定 default toolchain。

### 6.5 Docker Compose validation

Command:

```powershell
docker-compose -f infra/compose/docker-compose.yml config
```

Result:

- 成功

Notes:

- 本地環境支援 `docker-compose`
- 本地環境不支援 `docker compose`
- 因此本地驗證腳本已優先選擇 `docker-compose`，CI workflow 仍使用 GitHub-hosted runner 預期可用的 `docker compose`

### 6.6 Wrapper script validation

Command:

```powershell
.\scripts\verify-local.ps1
```

Result:

- 部分成功，部分失敗
- 最近一次執行結果為 `Passed: 5 / Failed: 5 / Skipped: 0`
- 成功項目：
  - Ruff
  - Pytest smoke
  - Web lint
  - Web typecheck
  - Docker compose config
- 失敗項目主要與上面一致：
  - mypy module / launcher 異常
  - unit / integration / e2e 的 Windows asyncio runtime 問題
  - cargo default toolchain 未設定

Command:

```bash
scripts/verify-local.sh
```

Result:

- 未在此 Windows sandbox 中直接執行
- 已完成功能對齊與內容校對，但缺少本地 Bash runtime 實測證據

## 7. Files changed in this governance pass

- `.gitignore`
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
- `package.json`
- `package-lock.json`
- `pyproject.toml`
- `uv.lock`

## 8. Remaining risks / follow-up

- 目前 repo 的大多數實作骨架仍是未追蹤狀態，未來第一個真正功能 PR 必須非常小心 staging 範圍。
- `README.md` 目前已有使用者未提交修改；這次治理變更沒有碰它。
- Python unit/integration/e2e 測試目前仍缺少乾淨的可重現通過證據。
- Rust 本地檢查仍依賴可用的 default toolchain 設定。
- `scripts/verify-local.sh` 尚未在本機 Bash 環境實測。

## 9. Conclusion

治理基線已建立完成，可以支撐後續以小 PR 方式逐步開發：

- 有 ignore baseline
- 有 CI baseline
- 有 advisory review baseline
- 有 CODEOWNERS / PR template / DoD / branching / workflow docs
- 有本地驗證入口與已知失敗面記錄

這一輪沒有做產品功能，不會改變既有 API、schema、UI、connector 行為。
