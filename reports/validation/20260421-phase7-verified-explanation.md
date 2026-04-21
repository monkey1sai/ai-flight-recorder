# Validation Report: Phase 7 Verified Explanation / Replay Gate

## Scope

Validate Product Phase 7 on top of the runnable MVP checkpoint:

- replay verification migration for `replay_runs` and `verification_records`
- repository-backed replay verification summary and refresh APIs
- worker helper for replay verification generation
- replay page rendering of verification badge, confidence, and replay-backed claim records
- compose-backed proof that the seeded `grade=verified` explanation is queryable through API and visible through `/replay/[traceId]`

## Commands run

```powershell
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_replay_verification.py tests/integration/test_api_operator_surfaces.py tests/e2e/test_observability_flow.py tests/smoke/test_operator_surfaces_assets.py -q
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check apps/api apps/web/lib apps/web/components apps/web/app/replay workers tests packages/schema
node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans
docker-compose -f infra/compose/docker-compose.yml config
docker-compose -f infra/compose/docker-compose.yml up --build -d
Invoke-WebRequest http://localhost:8080/api/v1/replay/22222222-2222-4222-8222-222222222222/verification | Select-Object -ExpandProperty Content
Invoke-WebRequest -Method Post http://localhost:8080/api/v1/replay/22222222-2222-4222-8222-222222222222/verify | Select-Object -ExpandProperty Content
(Invoke-WebRequest http://localhost:3000/replay/22222222-2222-4222-8222-222222222222).StatusCode
```

## Results

- `python -m pytest tests/unit/test_replay_verification.py tests/integration/test_api_operator_surfaces.py tests/e2e/test_observability_flow.py tests/smoke/test_operator_surfaces_assets.py -q`
  Passed. Covered replay verification derivation, operator API surface availability, seeded end-to-end replay consistency, and asset/report presence.
- `ruff check apps/api apps/web/lib apps/web/components apps/web/app/replay workers tests packages/schema`
  Passed.
- `pyright ... apps packages workers tests`
  Passed with `0 errors`.
- `npm run lint --workspace @aeris/web`
  Passed.
- `npm run typecheck --workspace @aeris/web`
  Passed.
- `docker-compose ... down -v --remove-orphans`
  Passed. Cleared prior Postgres/blob volumes so the new replay-verification migration was validated on a fresh DB.
- `docker-compose ... config`
  Passed.
- `docker-compose ... up --build -d`
  Passed. The stack rebuilt cleanly and the API bootstrapped with `0005_replay_verification_surfaces.up.sql`.
- `GET /api/v1/replay/22222222-2222-4222-8222-222222222222/verification`
  Passed with HTTP `200`. Returned:
  - `verification_badge="replay_verified"`
  - `verified_claim_count=1`
  - a `replay_run` with `frame_count >= 1`
  - at least one verification record carrying `evidence_grade="verified"` and a `replay_trace_id`
- `POST /api/v1/replay/22222222-2222-4222-8222-222222222222/verify`
  Passed with HTTP `200`. Rebuilt the same replay-backed verification summary through the explicit refresh route.
- `GET /replay/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200`. The replay page rendered the verification badge, confidence chip, and replay-backed claim list alongside step-by-step replay frames.

## Observed proof points

- Phase 7 stayed additive to the existing evidence model. Only explanations already marked `grade=verified` became replay verification records.
- The Web layer no longer needs to reverse-engineer replay provenance out of arbitrary explanation metadata; the replay route now returns a stable `ReplayVerificationView`.
- The seeded demo trace proves the end-to-end path without inventing unsupported verification: one claim remains replay-backed while the other remains only observed/supported elsewhere in the explanation stack.

## Remaining gaps

- This milestone does not introduce asynchronous replay scheduling or multi-run history. The repository keeps only the latest replay verification summary per trace.
- Counterfactual or ablation execution is still represented by existing explanation provenance, not a new execution engine.
- Confidence calibration remains basic. The summary exposes the highest replay-backed confidence; it does not yet run a separate calibration model.

## Failures

- None in the validated Phase 7 slice.

## Risk assessment

- Low product risk: the new verification surface is conservative and only promotes explanations already marked `verified`.
- Medium operational risk: replay verification currently refreshes synchronously and rewrites the latest per-trace summary, so it is not designed for concurrent job orchestration yet.
- Medium roadmap risk: future counterfactual infrastructure may require richer run metadata than the current MVP tables store, but the current contract is enough for the seeded/local slice.

## Recommendation

`ready_to_merge`

Reason:
- schema, repository, API, worker, web, and validation evidence are all present
- the feature is runnable on a fresh compose stack
- verification badge and replay-backed confidence are now backed by explicit persisted surfaces instead of UI-only inference

## Follow-up items

- Add asynchronous replay job scheduling only when the MVP needs concurrent or long-running verification.
- Preserve the current `verification_badge` / `replay_trace_id` contract if richer counterfactual metadata is added later.
- If later phases need confidence calibration, layer it onto `verification_records` rather than overwriting the explanation-grade contract.
