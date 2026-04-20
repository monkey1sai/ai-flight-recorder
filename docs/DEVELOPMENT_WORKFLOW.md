# Development Workflow

## Goal

用小範圍、可審查、可重跑的 PR 來演進 AERIS，不在單一變更中混入多個 concern。

## Standard Flow

1. 先讀 instruction chain：`AGENTS.md`、`COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`、`.agent/PLANS.md`、相關 active plan、必要 docs。
2. 執行 `git status --short` 與 `git diff`，確認目前工作樹與既有未提交變更。
3. 若任務非 trivial，先建立或更新 `plans/active/` ExecPlan，再開始修改。
4. 將變更限制在單一 concern；不要同時混入 product feature、治理、infra 與 unrelated cleanup。
5. 每完成一個安全停點就跑最小相關驗證，然後更新 plan 與報告。
6. 開 PR 前執行本地驗證腳本，補齊 PR template、風險說明、驗證證據與相關 docs。

## PR Size Expectations

- 一個 PR 只解決一個主要問題。
- 先求最小可驗證 slice，再往下一個 PR 擴充。
- 若變更跨越多個 subsystem，必須在 plan 中明寫 blast radius 與 rollback 邊界。

## Repository Hygiene

- 不提交 `node_modules/`、`.venv/`、cache、build outputs、`target/`、`.next/`。
- 不提交 `.env`、憑證、私鑰、user-local config、tokens。
- 任何機器相依設定若要留在 repo，必須先去除使用者路徑與憑證資訊。

## Validation Discipline

- 先跑最小相關測試，再擴大到 lint/typecheck/test。
- 若命令失敗，必須記錄失敗訊息、可能成因、是否為環境限制。
- 不可在沒有驗證證據的情況下宣告完成。
