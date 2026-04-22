# Live Google Drive Connector

## 1. Purpose / Big Picture

把目前 fixture-backed 的 Google Drive connector 升級成可在本機以真實 Google 帳號完成 OAuth、search、Docs 讀取/匯出、增量 change tracking、Drive Activity 查詢、並將結果持久化到既有 research store 的單一 phase。

這一輪的目標不是把整份 `總覽.md` 都做完，而是把 Drive 子項做成一個封閉、可直接驗收的 phase，讓人可以按驗收清單逐條確認功能已落地。

注意：目前 repo 內沒有名為 `總覽.md` 的檔案，因此這個 phase 的逐項驗收會以 `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` 第 12.3 節與 `docs/ACCEPTANCE_CHECKLIST.md` 的 Google Drive 子項作為實際對照來源，並在 validation report 明確標記這個 mapping。

成功的判斷標準：

- `AERIS_DRIVE_CONNECTOR_MODE=live` 時，repo 可以透過外部 `credentials.json` + 本機 token cache 完成 Installed App OAuth
- `/api/v1/research/drive/*` 能用真實 Drive/Docs/Drive Activity API 回傳資料
- search / sync / change tracking / activity 都會持久化到既有 research store
- `/research` 能清楚顯示 connector mode、授權狀態、sync/change/activity 驗收資訊
- validation report 可依實際可追溯的 Drive 驗收子項逐條列出 `passed / failed / blocked / not run`

## 2. Scope

In scope
- 新增 live Google Drive connector 與 Installed App OAuth
- 新增 env/config 與授權 bootstrap script
- 將 DI / service 從 fixture-only 改成 fixture/live connector selection
- 保留並擴充既有 research API 與持久化
- 新增 change tracking 與 Drive Activity query/sync API
- 新增 Drive Activity persistence migration
- 更新 `/research` 頁面為可驗收的 live Drive surface
- 補官方文件研究 note、ExecPlan、validation report、unit/integration/smoke tests

Out of scope
- `changes.watch` / `files.watch` webhook channels
- Web callback OAuth flow
- CI 非互動實帳驗收
- arXiv connector 變更
- replay / evals / hardening 相關工作

Assumptions
- 使用者會提供 repo 外部的 Google OAuth client secrets 檔案路徑
- token 允許存在 repo-ignore 的本機檔案路徑
- live 驗收在本機人工互動登入完成

Constraints
- 不讀取、輸出、提交任何 secrets / token 內容
- 只依賴官方 Google API 文件與現有參考 repo 的流程形狀，不複製憑證檔
- raw Docs JSON / 匯出內容寫到 blob store，不直接塞進 query table
- `ResearchDocumentRecord` 的 public wire shape 不做 breaking change

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `plans/active/20260421-mvp-phase-1-7-execution.md`
- `docs/ACCEPTANCE_CHECKLIST.md`
- `docs/research/20260422-google-drive-live-connector.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 12.3
- `docs/ACCEPTANCE_CHECKLIST.md` Google Drive subsection

## 3. Repository context

Relevant files and directories
- `apps/api/app/connectors/`
- `apps/api/app/services/research.py`
- `apps/api/app/dependencies.py`
- `apps/api/app/routers/research.py`
- `apps/api/app/repositories/`
- `apps/api/app/settings.py`
- `apps/api/app/storage.py`
- `apps/web/app/research/page.tsx`
- `apps/web/components/`
- `apps/web/lib/api.ts`
- `packages/schema/flight_recorder_schema/`
- `packages/schema/migrations/`
- `scripts/`
- `tests/`
- `reports/validation/`

Current repo state
- `FixtureDriveConnector` 是唯一 Drive connector
- `ResearchService` 與 `get_research_service()` 直接綁定 fixture connector
- 既有 Postgres/fixture repository 已能存 `research_documents`、`research_sync_runs`、`research_sync_cursors`
- `/research` 已能顯示 fixture-backed corpus 與 sync runs，但沒有 live auth status / change tracking / activity 驗收面
- 尚無 Google auth 相關依賴、設定、授權腳本、或 Drive Activity persistence

## 4. Success criteria

- settings 支援：
  - `AERIS_DRIVE_CONNECTOR_MODE=fixture|live|auto`
  - `AERIS_GOOGLE_CLIENT_SECRETS_PATH`
  - `AERIS_GOOGLE_TOKEN_PATH`
- 有可重複執行的 `scripts/authorize_google_drive.py`
- `GET /api/v1/research/drive/auth-status` 可明確回傳 mode、是否已授權、缺失原因
- `GET /api/v1/research/drive/search?q=...` 使用 live Drive `files.list`，一般文字 query 會走 `fullText contains`
- `POST /api/v1/research/drive/sync?q=...` 可對 Google Docs 做 `documents.get` 與 `files.export`，成功持久化 corpus
- 匯出超過 10 MB 或不支援時，sync 不失敗，並記錄 `export_status`
- `POST /api/v1/research/drive/changes/sync` 會建立或更新 `changes_page_token`
- `POST /api/v1/research/drive/activity/sync?source_id=...` 會持久化 activity
- `GET /api/v1/research/drive/activity?source_id=...` 可回傳 persisted activity
- `/research` 在 live mode 下可顯示 auth status、最近 sync、change token、activity
- validation report 依可追溯的 Drive 驗收子項逐條記錄結果

## 5. Milestones

### Milestone 0 - Research evidence and execution contract
Goal
- 把官方文件事實、phase 邊界、驗收標準落成可執行紀錄

Deliverables
- 本 ExecPlan
- Google Drive live connector research note

Validation method
- 檢查 plan 與 research note 完整度

### Milestone 1 - Auth and connector selection
Goal
- 建立 live/fixture mode、OAuth 設定、授權腳本、與 connector interface

Deliverables
- settings/env 擴充
- connector protocol / live connector auth bootstrap
- `authorize_google_drive.py`
- auth status API

Validation method
- targeted unit tests for settings / auth status
- script help/status smoke

Rollback / containment
- 若 live 設定缺失，`auto` 仍可安全 fallback 到 fixture

### Milestone 2 - Live Drive search and sync persistence
Goal
- 打通 live `files.list`、Docs JSON / export、及 corpus persistence

Deliverables
- live search/sync implementation
- blob persistence for Docs JSON/export payloads
- repository/service updates
- integration tests for sync persistence and export fallback

Validation method
- targeted unit/integration tests
- local API test client checks

Rollback / containment
- 保留 fixture connector 與既有 API shape

### Milestone 3 - Change tracking and activity persistence
Goal
- 實作增量 change tracking 與 Drive Activity query/sync

Deliverables
- migration for `research_drive_activity_events`
- repository methods and surface models
- `/drive/changes/sync` and `/drive/activity*` endpoints
- integration tests for token persistence and activity storage

Validation method
- migration tests
- targeted integration tests

Rollback / containment
- 不做 webhook/channel lifecycle，只做 pull-based sync

### Milestone 4 - Web acceptance surface and final validation
Goal
- 讓 `/research` 成為可直接驗收的 live Drive surface，並產出逐項驗收報告

Deliverables
- `/research` live Drive acceptance panels
- docs updates
- validation report with `passed / failed / blocked / not run`

Validation method
- web typecheck/lint
- smoke tests
- interactive live acceptance when credentials are available

## 6. Progress

- [x] 2026-04-22 02:25 UTC reread repo instructions, Phase 1-7 plan, and current research slice implementation
- [x] 2026-04-22 02:25 UTC created a clean worktree at `../AI-Flight-Recorder-drive-live` from `origin/master`
- [x] 2026-04-22 02:25 UTC created this ExecPlan and narrowed the work to the single Drive phase
- [x] 2026-04-22 02:40 UTC Milestone 0 complete: recorded official Drive/Docs/Drive Activity facts in `docs/research/20260422-google-drive-live-connector.md`
- [x] 2026-04-22 03:20 UTC Milestone 1 complete: added Drive mode selection, OAuth settings, auth-status API, and `scripts/authorize_google_drive.py`
- [x] 2026-04-22 04:05 UTC Milestone 2 complete: added live search/sync, Docs JSON export handling, and corpus persistence wiring
- [x] 2026-04-22 04:35 UTC Milestone 3 complete: added change tracking, Drive Activity persistence, migration `0006`, and API surface
- [x] 2026-04-22 05:35 UTC Milestone 4 complete: updated `/research` acceptance surface, refreshed repo docs, and recorded validation outcomes

## 7. Research notes

- Source: Google Drive API docs for changes and start page tokens
  Finding: change tracking can be implemented with `changes.getStartPageToken` and `changes.list`; `changes.watch` is optional and requires `pageToken`.
  Why it matters: this phase can satisfy the selected Drive change-tracking acceptance scope without webhook/channel lifecycle.
  Confidence: high

- Source: Google Drive downloads/export docs
  Finding: `files.export` exported content is limited to 10 MB.
  Why it matters: sync must degrade to `export_too_large` instead of failing the whole document ingestion.
  Confidence: high

- Source: Google Docs API docs
  Finding: `documents.get` is available with `documents.readonly`.
  Why it matters: Google Docs JSON can be retrieved separately from Drive metadata/export.
  Confidence: high

- Source: Drive Activity API v2 docs
  Finding: `activity.query` supports `itemName = items/{ITEM_ID}` and `drive.activity.readonly`.
  Why it matters: per-document activity sync can be implemented without scanning the whole Drive.
  Confidence: high

## 8. Surprises & Discoveries

- The existing repository shape is already close to live Drive support because research persistence, sync runs, and cursors are already modeled.
- The biggest missing pieces are not storage, but auth/config selection and a second persistence table for activity events.
- The repo-level acceptance source named by the request (`總覽.md`) does not exist in this checkout, so the validation surface needs an explicit mapping to the project guide and acceptance checklist.

## 9. Decision log

- 2026-04-22: implement this work as a standalone Drive phase on a clean worktree instead of reusing the dirty local checkout.
  Rationale: the user explicitly wants a single phase with direct acceptance, and the main checkout already contains unrelated local state.
  Alternatives rejected: editing directly on the dirty `master` tree.

- 2026-04-22: use Installed App OAuth with external credential file paths.
  Rationale: it matches the provided reference repo and is the smallest path to interactive real-account acceptance.
  Alternatives rejected: callback-based OAuth flow; service account flow.

- 2026-04-22: implement pull-based change tracking with `startPageToken + changes.list`, not `watch`.
  Rationale: this meets the selected acceptance scope while keeping the phase bounded.
  Alternatives rejected: adding webhook/channel lifecycle in the same phase.

- 2026-04-22: treat `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 12.3 plus `docs/ACCEPTANCE_CHECKLIST.md` as the effective acceptance source for Drive.
  Rationale: the requested `總覽.md` file is absent from the repository, but the Drive requirements and checklist items are still available in tracked docs.
  Alternatives rejected: fabricating a new top-level `總覽.md` during implementation.

## 10. Validation plan

- `uv run python -m pytest tests/unit/test_drive_live_auth.py tests/unit/test_research_connector_sync.py -q`
- `uv run python -m pytest tests/integration/test_api_operator_surfaces.py -q`
- `uv run python -m pytest tests/smoke/test_operator_surfaces_assets.py -q`
- `uv run ruff check apps/api apps/web/lib apps/web/components apps/web/app/research scripts tests packages/schema`
- `node ./node_modules/pyright/index.js --pythonpath ./.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests`
- `npm run lint --workspace @aeris/web`
- `npm run typecheck --workspace @aeris/web`
- live acceptance:
  - `python scripts/authorize_google_drive.py`
  - `Invoke-WebRequest http://localhost:8080/api/v1/research/drive/auth-status`
  - `Invoke-WebRequest http://localhost:8080/api/v1/research/drive/search?q=...`
  - `Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/drive/sync?q=...`
  - `Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/drive/changes/sync`
  - `Invoke-WebRequest -Method Post http://localhost:8080/api/v1/research/drive/activity/sync?source_id=...`
  - `Invoke-WebRequest http://localhost:8080/api/v1/research/drive/activity?source_id=...`
  - `Invoke-WebRequest http://localhost:8080/api/v1/research/corpus?source_type=drive`
  - `Invoke-WebRequest http://localhost:3000/research`

## 11. Risks / Blockers

- Live OAuth and acceptance are blocked until the user provides a valid external client secrets file.
- The new Google libraries may expand dependency/lockfile maintenance work.
- Interactive local OAuth may be difficult to run inside some headless/container contexts; keep the acceptance path host-local.

## 12. Deliverables

- `plans/active/20260422-live-google-drive-connector.md`
- `docs/research/20260422-google-drive-live-connector.md`
- live Drive connector/auth/config changes
- migration for Drive activity persistence
- API/web/test updates
- `reports/validation/20260422-live-google-drive-connector.md`

## 13. Completion note

Shipped
- live/fixture/auto Drive connector selection with explicit auth-status surface
- Installed App OAuth bootstrap script with repo-ignore token path support
- live Drive search, Docs JSON hydration, export fallback, incremental changes sync, and per-document activity sync
- Drive activity persistence migration plus repository/service/API support
- `/research` acceptance panel for auth, sync, change tracking, and activity
- unit/integration/smoke coverage, repo validation gates, and final validation report

Did not ship
- interactive live-account acceptance execution, because no external OAuth client secrets were provided in this session

Follow-up
- if future work needs push notifications, add `changes.watch` / `files.watch` in a separate phase
