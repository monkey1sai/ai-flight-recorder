# Validation Report: Live Google Drive Connector

## Scope

- Branch/worktree: `feat/live-google-drive-connector` in `C:\Repos\active\ai-agent\AI-Flight-Recorder-drive-live`
- Scope validated here:
  - Drive connector mode selection: `fixture | auto | live`
  - Installed App OAuth bootstrap script and auth-status surface
  - live Drive search, Docs JSON hydration, export fallback, change tracking, and activity persistence
  - `/research` acceptance surface for Drive auth/sync/change/activity
- Acceptance-source note:
  - The requested `總覽.md` file is not present in this repository checkout.
  - This report therefore maps acceptance against:
    - `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section `12.3 Google Drive 連接器規格`
    - `docs/ACCEPTANCE_CHECKLIST.md` subsection `D. Research connectors / Google Drive`

## Commands run

```powershell
uv run python -m pytest tests/unit/test_drive_live_auth.py tests/unit/test_research_connector_sync.py -q
uv run python -m pytest tests/integration/test_api_operator_surfaces.py -q
uv run python -m pytest tests/smoke/test_operator_surfaces_assets.py -q
uv run ruff check apps/api apps/web/lib apps/web/components apps/web/app/research scripts tests packages/schema
node ./node_modules/pyright/index.js --pythonpath ./.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
```

## Results

### Automated validation

- `tests/unit/test_drive_live_auth.py tests/unit/test_research_connector_sync.py -q`: passed
- `tests/integration/test_api_operator_surfaces.py -q`: passed
- `tests/smoke/test_operator_surfaces_assets.py -q`: passed
- `uv run ruff check apps/api apps/web/lib apps/web/components apps/web/app/research scripts tests packages/schema`: passed
- `node ./node_modules/pyright/index.js --pythonpath ./.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests`: passed
- `npm run lint --workspace @aeris/web`: passed
- `npm run typecheck --workspace @aeris/web`: passed

### Acceptance mapping

From `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md` section 12.3 and `docs/ACCEPTANCE_CHECKLIST.md`:

| Item | Status | Evidence |
| --- | --- | --- |
| Search queries are recorded or reproducible | passed | `build_drive_files_query()` uses reproducible `fullText contains` clauses; query/cursor persisted in research provenance and sync runs |
| Export size limits are handled | passed | export HTTP failure is classified to `export_too_large` / `export_unavailable` / `export_failed`; sync does not fail the whole document |
| Change tracking is incremental | passed | `changes.getStartPageToken` + `changes.list` implemented with persisted `changes_page_token` cursor |
| Activity fields are mapped when required | passed | Drive Activity query maps timestamp, primary action, actors, targets, raw payload ref, then persists to `research_drive_activity_events` |
| Tests use fixtures or mocks when live credentials are unavailable | passed | unit/integration/smoke coverage runs entirely on fixture backend without requiring live OAuth credentials |
| Installed App OAuth with external credential file | passed | `scripts/authorize_google_drive.py` + auth-status API + env-based credential/token paths |
| `/research` exposes auth / sync / change / activity acceptance state | passed | page renders `DriveLiveAcceptancePanel` with auth status, latest sync, change receipt, and per-document activity |
| Interactive real-account acceptance | blocked | no external Google OAuth client secrets were provided during this session, so live end-to-end authorization could not be executed |

## Failures

- No confirmed functional failures in the automated fixture-backed validation set.
- Live-account acceptance remains blocked by missing external credentials, so real Drive API execution is not claimed as completed.
- `npm install --workspaces --include-workspace-root` reported one high-severity audit finding in the workspace dependency tree. This report did not expand that audit because it is outside the Drive feature diff and did not block validation execution.

## Risk assessment

- Medium residual risk on live OAuth/runtime behavior until a real `credentials.json` is supplied and the interactive acceptance steps are executed.
- Low risk on API/data-shape regressions for fixture/default mode because unit/integration/smoke coverage passed against the updated surfaces.
- Medium repo-health risk remains if lint/typecheck expose pre-existing environment issues outside this change surface; those need to be separated from new defects before merge.

## Recommendation

- `merge_with_known_risks` if the branch is being accepted for code completion of the Drive phase but live-account acceptance is deferred until credentials are available.
- `not_ready` if the acceptance bar explicitly requires successful interactive Google OAuth and real Drive API calls in the same session.

## Current verdict

- Code implementation status: ready for code review
- Automated validation status: passed
- Interactive live-account acceptance status: blocked by missing credentials

## Follow-up items

- Run `python scripts/authorize_google_drive.py` with a real external `AERIS_GOOGLE_CLIENT_SECRETS_PATH`.
- Execute the live acceptance flow from the ExecPlan and append the concrete outputs to this report.
- If needed later, add webhook-based `changes.watch` / `files.watch` in a separate phase instead of expanding this one.
