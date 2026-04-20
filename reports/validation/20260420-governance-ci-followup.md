# Governance CI Follow-up

## Scope

修正 PR `#1` 上 `CI` workflow 的 4 個失敗 check：

- `docker-compose`
- `node`
- `python`
- `rust`

範圍只限於 `.github/workflows/ci.yml`，不補提交流程以外的 product skeleton 檔案。

後續追加修正 `Codex Advisory Review` workflow 的紅燈問題，範圍只限於 `.github/workflows/codex-review.yml`。

## Commands run

```powershell
git -c safe.directory=C:/Repos/active/ai-agent/AI-Flight-Recorder diff -- .github/workflows/ci.yml
git -c safe.directory=C:/Repos/active/ai-agent/AI-Flight-Recorder status --short .github/workflows/ci.yml
```

GitHub evidence gathered via connector:

- fetched workflow run jobs for run `24651427962`
- fetched job logs for:
  - `72074889185` (`docker-compose`)
  - `72074889189` (`python`)
  - `72074889197` (`rust`)
  - `72074889204` (`node`)
- fetched OpenAI official docs for `openai/codex-action@v1` troubleshooting and prerequisites

## Results

### Confirmed root cause

從 GitHub Actions logs 可確認 4 個失敗都不是程式碼測試失敗，而是 workflow 在 PR checkout 內容中找不到預期檔案：

- `docker-compose`: `infra/compose/docker-compose.yml` not found
- `python`: `No pyproject.toml found in current directory or any parent directory`
- `rust`: `edge/daemon/Cargo.toml` does not exist
- `node`: `cache-dependency-path: package-lock.json` could not be resolved

這與本地稽核一致：目前工作樹裡大量 product skeleton 仍未追蹤，所以 GitHub 在 PR merge ref 上拿到的是較小的版本化快照。

### Fix applied

在 `.github/workflows/ci.yml`：

- 新增 `component-presence` job
- 先 checkout 後檢查這些 versioned files 是否存在：
  - `pyproject.toml`
  - `package.json`
  - `package-lock.json`
  - `apps/web/package.json`
  - `edge/daemon/Cargo.toml`
  - `infra/compose/docker-compose.yml`
- 讓 `python` / `node` / `rust` / `docker-compose` jobs 只有在對應檔案存在時才執行
- `push.branches` 補上 `master`，避免 repo 預設分支合併後不觸發 CI

另外在 `.github/workflows/codex-review.yml`：

- 移除 `pull-requests: write`
- 保留 `contents: read` 與 `issues: write`

這和目前 workflow 實作一致，因為它只會：

- 讀取 PR merge ref
- 執行 read-only Codex review
- 用 `github.rest.issues.createComment(...)` 貼一則 PR conversation comment

### Advisory review failure analysis

目前紅燈 log 的關鍵訊息是：

- repeated `ENOENT` while reading `/home/runner/.codex/<run-id>.json`

根據 OpenAI 官方文件 `Codex GitHub Action -> Troubleshooting`：

- `responses-api-proxy didn't write server info`: confirm the API key is present and valid; the proxy starts only when you provide `openai-api-key`

這表示失敗點屬於 action 執行環境／secret 狀態，不是 repo 內容回歸。

### Additional fix applied

在 `.github/workflows/codex-review.yml`：

- 新增 `codex_preflight` job 檢查 `OPENAI_API_KEY` 是否存在
- 只有在：
  - PR 不是 draft
  - PR head repo 等於 base repo
  - `OPENAI_API_KEY` 存在
  時才執行 `codex_review`
- 將 `Run Codex advisory review` 設為 `continue-on-error: true`
- 若 action 本身失敗，改發 workflow warning，不再讓 advisory review 變成阻擋 PR 的紅燈

這樣的行為符合此 workflow 的設計定位：`advisory-only`

### Local evidence

- `git diff` 顯示 `ci.yml` 已加入 presence-gating 與 `master` push trigger
- `git status` 顯示只有 `.github/workflows/ci.yml` 被修改
- `git diff` 顯示 `codex-review.yml` 已加入 secret preflight 與 non-blocking fallback

## Failures

- 無法在本地直接重新執行 GitHub-hosted workflow，因此不能在這個 sandbox 內取得修補後的新 run 結果
- 本機沒有可用的 YAML lint 工具；PowerShell 也沒有 `ConvertFrom-Yaml`，因此本次採用人工 diff 檢查與 GitHub log 對位驗證
- 即使加入 preflight，若 `OPENAI_API_KEY` 存在但值無效，`openai/codex-action` 仍可能失敗；本次改動選擇讓這類 advisory failure 降級為 warning，而不是繼續阻擋 PR

## Risk assessment

- 低風險：改動只影響 workflow 條件分流，不碰產品碼
- 低風險：對已完整 versioned 的後續 PR，不會跳過原本該跑的 job
- 中風險：若未來 job 的前置條件改變，`component-presence` 的檔案探針需要同步維護
- 低風險：Codex review 失敗時不再紅燈，但也代表 secret 配置錯誤可能只以 warning 形式暴露，需要 maintainer 主動查看

## Recommendation

`merge_with_known_risks`

理由：

- 這次修補已對準目前 PR 的實際失敗原因
- 但仍需 push 後由 GitHub 實際跑一次 workflow，才能把風險從「推理成立」降到「已驗證成立」

## Follow-up items

- push 此修補後重新查看 PR checks，確認 4 個 job 轉為 `skipped` 或在元件存在時正常執行
- push 此修補後重新查看 `Codex Advisory Review`，確認它在 draft / missing-secret / transient proxy failure 情況下不再以 failed conclusion 阻擋 PR
- 後續若把 product skeleton 逐步納入版本控制，保留這個 presence-gating 設計，讓 CI 對 repo 演進更耐受
