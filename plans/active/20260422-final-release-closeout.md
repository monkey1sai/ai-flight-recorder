# Final Release Closeout

## 1. Purpose / Big Picture

把目前 `master` 已知、可在 repo 內直接修掉的 live Google Drive 驗收 blocker 收斂成最後一個可 review PR，讓專案進到真正可交付的收尾狀態。

這次不是再擴 scope 做新功能，而是把已驗出的 closeout 缺口補齊：

- Docker API image 缺少 live Drive 依賴
- compose stack 沒有正式支援 live Drive env 契約
- fixture 時代留下的 change cursor 會污染第一次 live `changes/sync`
- 外部 Google API 未啟用時，系統目前回 500，不利驗收與故障判讀

成功標準不是「替外部 Google Cloud 專案啟用 API」，而是：

- repo 本身不再因缺依賴或錯誤初始化而失敗
- 外部 API disabled / permission 問題能被明確 surfaced 為可驗收的 blocked 狀態
- 預設 compose stack 可以吃 live Drive env 直接啟動
- `/research` 驗收面與 API 回應能把 repo defect 與外部 blocker 清楚分開

## 2. Scope

In scope
- API Docker image 補齊 live Drive 所需 Google auth runtime 依賴
- `infra/compose/docker-compose.yml` 補齊 live Drive env 與 credentials/token mount 契約
- live `changes/sync` 的 cursor hygiene，避免 fixture cursor 汙染 live token
- 對 Docs API / Drive Activity API disabled 或 permission 類錯誤做明確 blocker surfacing
- `/research` 驗收面在 live mode 下顯示真實 blocked state，而不是 generic failure
- 補 unit/integration/smoke tests、validation report、plan 更新

Out of scope
- 啟用 Google Cloud 專案的 Docs API / Drive Activity API
- 新增 webhook / watch channel
- 新增新的 research connector
- 大規模重構 `/research` 頁面資料流
- 重新設計 Google Drive search semantics

Assumptions
- 使用者可接受這次 PR 只修 repo 內缺口，不包含外部 Google Console 操作
- `credentials.json` 與 token 仍採外部檔案 / repo-ignore 契約

Constraints
- 不輸出任何 secrets / token 內容
- 不修改 `.codex/` / `.agents/`
- 保持現有 public API shape 盡量穩定，若要新增欄位需為向後相容

Dependencies
- `AGENTS.md`
- `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
- `.agent/PLANS.md`
- `plans/active/20260422-live-google-drive-connector.md`
- `reports/validation/20260422-live-drive-real-account-acceptance.md`
- `docs/ACCEPTANCE_CHECKLIST.md`

## 3. Repository context

Relevant files
- `infra/docker/api.Dockerfile`
- `infra/compose/docker-compose.yml`
- `apps/api/app/connectors/drive.py`
- `apps/api/app/services/research.py`
- `apps/api/app/routers/research.py`
- `apps/api/app/repositories/postgres_store.py`
- `apps/web/app/research/page.tsx`
- `apps/web/lib/api.ts`
- `apps/web/components/drive-live-acceptance-panel.tsx`
- `tests/unit/test_drive_live_auth.py`
- `tests/unit/test_research_connector_sync.py`
- `tests/integration/test_api_operator_surfaces.py`
- `tests/smoke/test_operator_surfaces_assets.py`

Current observed gaps from acceptance
- API image requires ad-hoc `pip install google-auth ...` to run live acceptance
- compose `api` service does not forward Drive env vars or credentials/token mount
- first live `changes/sync` can consume `drive-fixture:*` token from `research_sync_cursors`
- Docs API disabled and Drive Activity API disabled currently surface as server 500s
- default compose web route does not serve live acceptance without manual environment wiring

## 4. Success criteria

- `infra/docker/api.Dockerfile` includes the Google auth runtime dependencies needed by `LiveDriveConnector`
- `docker-compose -f infra/compose/docker-compose.yml config` remains valid after adding live Drive env contract
- compose `api` service can read:
  - `AERIS_DRIVE_CONNECTOR_MODE`
  - `AERIS_GOOGLE_CLIENT_SECRETS_PATH`
  - `AERIS_GOOGLE_TOKEN_PATH`
- first live `POST /api/v1/research/drive/changes/sync` no longer fails just because a fixture cursor exists
- when Google Docs API or Drive Activity API is disabled, API responses are explicit and non-generic; they identify the blocked reason
- `/research` shows the blocked state clearly in live mode rather than silently falling back
- tests cover:
  - live cursor hygiene
  - API blocker surfacing
  - compose-driven live env behavior where feasible
- validation note documents what is now fixed vs. what still depends on external Google project configuration

## 5. Milestones

### Milestone 1 - Runtime and compose contract
Goal
- remove the environment/bootstrap defects that currently block standard live acceptance

Deliverables
- updated API Dockerfile
- updated compose env / mount contract

Validation method
- `docker-compose ... config`
- targeted tests if needed

### Milestone 2 - Live Drive hardening
Goal
- make live Drive behavior safe under mixed fixture/live persisted state and external API disablement

Deliverables
- cursor hygiene fix
- explicit blocker/error mapping for Docs and Activity APIs
- any minimal schema/type additions required for non-breaking surfaced state

Validation method
- targeted unit/integration tests

### Milestone 3 - Web acceptance and release evidence
Goal
- ensure `/research` represents live blocked states correctly and record final release evidence

Deliverables
- web data-flow or UI adjustments if required
- validation report

Validation method
- relevant tests
- manual/HTTP smoke on `/research`

## 6. Progress

- [x] 2026-04-22 04:48 UTC reread repo contract, active Drive plan, and real-account acceptance report
- [x] 2026-04-22 04:52 UTC created this final closeout ExecPlan and narrowed scope to repo-controlled release blockers
- [x] 2026-04-22 05:15 UTC Milestone 1 complete: API Docker image now includes Google auth runtime deps, and compose exposes the live Drive env/token contract
- [x] 2026-04-22 05:35 UTC Milestone 2 complete: live change-sync ignores fixture cursor residue, Docs API disablement no longer aborts sync, and Drive Activity disablement is surfaced as an explicit blocked state
- [x] 2026-04-22 05:55 UTC Milestone 3 complete: `/research` acceptance panel renders blocked reasons, targeted tests were updated, and repo validation gates passed

## 7. Research notes

- Source: `reports/validation/20260422-live-drive-real-account-acceptance.md`
  Finding: repo-level blockers are distinct from Google Cloud project blockers; the former are Docker/compose/cursor-hygiene issues, the latter are disabled Docs API and Drive Activity API.
  Why it matters: this PR should only claim to fix repo-level blockers.
  Confidence: high

## 8. Surprises & Discoveries

- The live connector itself already proved OAuth, search, sync, corpus persistence, and live UI rendering.
- The remaining failure surface is mostly release-hardening, not connector design.

## 9. Decision log

- 2026-04-22: do the final closeout as one bounded PR instead of reopening a larger new phase.
  Rationale: the remaining work is hardening and acceptance closure, not a new product slice.
  Alternatives rejected: bundling replay/evals work or unrelated cleanup into the final PR.

## 10. Validation plan

- targeted:
  - `uv run python -m pytest tests/unit/test_drive_live_auth.py tests/unit/test_research_connector_sync.py -q`
  - `uv run python -m pytest tests/integration/test_api_operator_surfaces.py -q`
  - `uv run python -m pytest tests/smoke/test_operator_surfaces_assets.py -q`
- repo gates:
  - `make lint`
  - `make typecheck`
  - `make test`
- manual smoke:
  - `docker-compose -f infra/compose/docker-compose.yml config`
  - `curl.exe -sS http://127.0.0.1:8080/api/v1/research/drive/auth-status`
  - `curl.exe -sS -X POST http://127.0.0.1:8080/api/v1/research/drive/changes/sync`
  - `curl.exe -sS http://127.0.0.1:3000/research`

## 11. Risks / Blockers

- External Google project API enablement remains outside repo control.
- Existing local dirty state in this worktree must not be reverted accidentally.
- compose validation may need temporary container restarts; keep changes limited and documented.

## 12. Deliverables

- code changes in API / compose / web / tests
- updated active ExecPlan
- validation note under `reports/validation/`

## 13. Completion note

Shipped
- API runtime now bundles the Google auth libraries required by `LiveDriveConnector`
- compose can run the API/Web stack in live Drive mode with a stable env and token mount contract
- first live `changes/sync` ignores stale `drive-fixture:*` cursors instead of poisoning the session
- Docs API disablement is recorded in document provenance metadata and no longer hard-fails the whole sync path
- Drive Activity API disablement is surfaced through explicit blocked reasons in API and `/research`
- repo validation gates passed locally, and `docker-compose ... build api web` completed successfully

Still external
- Google Docs API and Drive Activity API must still be enabled in the target Google Cloud project for full real-account acceptance
