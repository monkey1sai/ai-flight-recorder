# Validation Report: Final Release Closeout

## Scope

- Branch baseline: local `master` after the merged live Google Drive connector phase
- Goal: close the remaining repo-controlled release blockers found in `reports/validation/20260422-live-drive-real-account-acceptance.md`
- In scope:
  - API Docker runtime dependencies for live Drive
  - compose env / token mount contract for live Drive acceptance
  - fixture cursor hygiene for first live `changes/sync`
  - explicit blocked-state surfacing for Google Docs API and Drive Activity API failures
  - `/research` acceptance panel updates for blocked states
- Out of scope:
  - enabling Google APIs in the external Google Cloud project
  - replay / evals / unrelated phase work

## Changes validated

### Runtime and compose contract

- `infra/docker/api.Dockerfile`
  - now installs `google-auth`, `google-auth-oauthlib`, and `requests`
- `infra/compose/docker-compose.yml`
  - now forwards:
    - `AERIS_DRIVE_CONNECTOR_MODE`
    - `AERIS_GOOGLE_CLIENT_SECRETS_PATH`
    - `AERIS_GOOGLE_TOKEN_PATH`
  - now mounts:
    - `tmp/google-auth` to `/var/lib/aeris/google-auth`
    - repo root read-only to `/workspace-host`
  - web now accepts `NEXT_PUBLIC_API_BASE_URL` override

### Live Drive hardening

- `apps/api/app/services/research.py`
  - first live `changes/sync` now ignores stale `drive-fixture:*` `changes_page_token` values
- `apps/api/app/connectors/drive.py`
  - Google Docs API failures no longer abort document hydration
  - Docs failures are preserved in provenance metadata with explicit blocked reasons
  - Drive Activity API failures now return blocked-state surfaces instead of generic server failures
- `packages/schema/flight_recorder_schema/surfaces.py`
  - change/activity surfaces now support `blocked_reason` and `metadata_json`

### Web acceptance surface

- `apps/web/app/research/page.tsx`
  - now keeps both activity sync receipt and activity list state
- `apps/web/components/drive-live-acceptance-panel.tsx`
  - now renders blocked reasons for change tracking and activity
- `apps/web/lib/api.ts`
  - live-mode fetch failures now surface explicit `upstream_unavailable` states instead of fixture-like ambiguity

## Commands run

```powershell
uv run python -m pytest tests/unit/test_drive_live_auth.py tests/unit/test_research_connector_sync.py -q
uv run python -m pytest tests/integration/test_api_operator_surfaces.py -q
uv run python -m pytest tests/smoke/test_operator_surfaces_assets.py -q
uv run python -m pytest tests/unit tests/integration tests/e2e tests/smoke -q

docker-compose -f infra/compose/docker-compose.yml config
docker-compose -f infra/compose/docker-compose.yml build api web

uv run ruff check .
node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests
cargo check --manifest-path edge/daemon/Cargo.toml
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
```

## Results

| Check | Status | Evidence |
| --- | --- | --- |
| Targeted unit tests | passed | `12 passed` |
| Targeted integration tests | passed | `7 passed` |
| Full local test suite | passed | `37 passed` across `tests/unit tests/integration tests/e2e tests/smoke` |
| Ruff | passed | `All checks passed!` |
| Pyright | passed | `0 errors, 0 warnings, 0 informations` |
| Cargo check | passed | `Finished 'dev' profile` |
| Web lint | passed | `eslint .` completed successfully |
| Web typecheck | passed | `tsc --noEmit` completed successfully |
| Compose config | passed | `docker-compose ... config` rendered a valid merged config with live Drive envs and mounts |
| Compose image build | passed | `docker-compose ... build api web` completed successfully |

## Acceptance impact

### Fixed repo-controlled blockers

| Previous blocker | Status after closeout | Evidence |
| --- | --- | --- |
| API image missing Google auth dependencies | fixed | API Docker build now includes `google-auth`, `google-auth-oauthlib`, and `requests` |
| compose stack lacked a stable live Drive contract | fixed | `docker-compose ... config` shows live envs and token mount wiring |
| first live `changes/sync` could consume fixture cursor residue | fixed | unit/service coverage now verifies fixture cursor residue is ignored in live mode |
| Docs API disablement caused generic sync failure | fixed | unit coverage shows hydration continues, export still succeeds, and provenance records `docs_api_disabled` |
| Drive Activity disablement surfaced as generic failure | fixed | integration coverage now verifies `drive/activity/sync` returns `blocked_reason=drive_activity_api_disabled` |
| `/research` could hide live blocked states behind empty/fallback views | fixed | UI now renders blocked reasons for change tracking and activity paths |

### Still external

| Item | Status | Why |
| --- | --- | --- |
| Google Docs API enablement in the target Google Cloud project | blocked_external | cannot be fixed inside this repo |
| Drive Activity API enablement in the target Google Cloud project | blocked_external | cannot be fixed inside this repo |

## Remaining risks

- The compose contract assumes local real-account acceptance uses:
  - repo root `credentials.json` mounted read-only at `/workspace-host/credentials.json`
  - `tmp/google-auth/` for token persistence
- `docker-compose ... build web` reported one upstream `npm audit` high severity vulnerability during install output. This PR does not change dependency selection or attempt an unrelated audit fix.
- Full real-account rerun was not repeated in this closeout pass because the last recorded blocker is now external Google API enablement rather than repo code.

## Recommendation

`ready_to_merge`

Interpretation:

- This PR fixes the remaining **repo-controlled** release blockers discovered during live Drive acceptance.
- After merge, the repository is in a clean handoff state for final acceptance.
- The remaining failure surface is explicitly external:
  - enable Google Docs API
  - enable Drive Activity API
  - rerun the real-account acceptance checklist
