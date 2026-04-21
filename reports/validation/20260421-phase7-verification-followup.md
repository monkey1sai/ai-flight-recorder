# Validation Report: Phase 7 Replay Verification Follow-up

## Scope

Validate the post-merge follow-up fix for Phase 7:

- stop upgrading summary `verification_badge` to `replay_verified` when a verified explanation has no `replay_trace_id`
- stop generating synthetic `completed` replay runs when a trace has no replay-backed verification evidence
- preserve explicit `0.0` explanation confidence instead of falling back to claim confidence

## Commands run

```powershell
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/unit/test_replay_verification.py -q
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check apps/api tests packages/schema
node C:/Repos/active/ai-agent/AI-Flight-Recorder/node_modules/pyright/index.js --pythonpath C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -p pyrightconfig.json --level error apps packages workers tests
```

## Results

- `python -m pytest tests/unit/test_replay_verification.py -q`
  Passed. `4 passed`.
  Covered:
  - replay-backed seed path still produces `replay_verified`
  - missing `replay_trace_id` now downgrades the summary to `verified_without_replay_ref`
  - zero verified explanations now yield `no_replay_evidence` with `replay_run is None`
  - explicit `0.0` confidence is preserved
- `ruff check apps/api tests packages/schema`
  Passed.
- `pyright ... apps packages workers tests`
  Passed with `0 errors`.

## Failures

- None in this follow-up scope.

## Risk assessment

- Low product risk: the fix narrows the Phase 7 claim surface and removes overclaim behavior.
- Low implementation risk: the change stays inside replay verification derivation and unit coverage now locks the edge cases directly.
- Remaining scope boundary: this follow-up does not add any new replay execution capability; it only corrects how existing replay provenance is summarized.

## Recommendation

`ready_to_merge`

## Follow-up items

- If future phases introduce true asynchronous replay execution, keep the invariant that `replay_run` only exists when the system can point to concrete replay provenance.
- If UI ever needs to distinguish replay-backed vs non-replay verified explanations more prominently, use the existing `verification_badge` split instead of parsing explanation metadata ad hoc.
