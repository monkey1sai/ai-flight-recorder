# Code Review Feedback — replay verification recursion fix

Date (UTC): 2026-04-21
Reviewed commit: `96c2f51c0b18aadec9162886d9209459bd71e39b`
Reviewer: Codex

## Scope reviewed

- `apps/api/app/repositories/fixture_store.py`
- `apps/api/app/repositories/postgres_store.py`
- `tests/integration/test_api_operator_surfaces.py`

## Summary

- ✅ The recursion hazard is addressed cleanly by replacing `get -> refresh -> get` flow with direct view materialization helpers in both fixture and Postgres repositories.
- ✅ Replay verification state handling is safer: fixture store now clears stale replay-run rows when `view.replay_run` is absent.
- ✅ Integration coverage now asserts the replay verification endpoint behavior for claimless ingest (`verification_badge=no_replay_evidence`, `replay_run=null`).
- ℹ️ No blocking defects were identified in this patch.

## Detailed feedback

1. **Good: recursion removed without changing API shape**
   - The new `_materialize_replay_verification_view(...)` helper avoids recursive read-refresh cycles and keeps response assembly deterministic in memory.
   - This is implemented consistently across fixture and Postgres repositories, which reduces drift risk between environments.

2. **Good: stale replay run cleanup in fixture path**
   - `_replace_replay_verification(...)` now explicitly removes replay-run state when a refreshed view has no replay run. This prevents old run metadata from leaking into later reads.

3. **Good: regression-oriented integration assertion**
   - The operator-surface integration test now checks the replay verification endpoint in the same claimless scenario that validates why derivation fallback.
   - This directly guards the over-claiming behavior that the fix targets.

## Residual risk (non-blocking)

- The current test asserts one claimless path. If desired later, add one extra integration case that starts from a previously verified replay state and then refreshes to an unverified state, to ensure badge/run transitions remain stable across updates.

## Validation commands run

- `pytest -q tests/integration/test_api_operator_surfaces.py::test_normalized_ingest_derives_unsupported_why_records_when_claims_absent`
  - Result: could not execute in this environment because `fastapi` is not installed.
