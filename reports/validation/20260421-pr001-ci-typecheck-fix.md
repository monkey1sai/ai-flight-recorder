# PR-001 CI Typecheck Fix

## Scope

修正 PR-001 (`codex/p1-monorepo-skeleton-validation`) 在 GitHub Actions 無法 merge 的 `python` job 失敗問題。範圍限於讓 Python typecheck 從不可攜的本機 shim 改為 repo 內可重現的實作，並重新驗證這個變更沒有破壞既有的 Python / Node / Rust skeleton gates。

## Commands run

```powershell
uv run mypy apps packages workers tests
.venv\Scripts\mypy.exe --version
uv run python -m mypy --version
node node_modules\pyright\index.js --help
node .\node_modules\pyright\index.js -p pyrightconfig.json --level error apps packages workers tests
npm run typecheck:python
uv run ruff check .
uv run python -m pytest tests/unit -q -p no:cacheprovider
uv run python -m pytest tests/integration -q -p no:cacheprovider
uv run python -m pytest tests/e2e -q -p no:cacheprovider
uv run python -m pytest tests/smoke -q -p no:cacheprovider
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
cargo check --manifest-path edge/daemon/Cargo.toml
uv sync --group dev
npm ci --workspaces --include-workspace-root
```

## Results

### Passed

- `node .\node_modules\pyright\index.js -p pyrightconfig.json --level error apps packages workers tests`
- `npm run typecheck:python`
- `uv run ruff check .`
- `uv run python -m pytest tests/unit -q -p no:cacheprovider`
- `uv run python -m pytest tests/integration -q -p no:cacheprovider`
- `uv run python -m pytest tests/e2e -q -p no:cacheprovider`
- `uv run python -m pytest tests/smoke -q -p no:cacheprovider`
- `npm run lint --workspace @aeris/web`
- `npm run typecheck --workspace @aeris/web`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `uv sync --group dev`

### Failed

- `uv run mypy apps packages workers tests`
  - failure mode 1 on GitHub-hosted Windows runner: `Global pyright installation not found for the offline mypy shim.`
  - failure mode 2 on this workstation: the shim falls through to global `pyright` and still mis-resolves imports until pyright is given explicit repo config
- `uv run python -m mypy --version`
  - failed with `No module named mypy`
  - confirms the vendored `mypy` wheel is not upstream mypy
- `npm ci --workspaces --include-workspace-root`
  - failed locally with Windows `spawn EPERM`
  - this did not reproduce on the earlier `npm install --save-dev pyright`, nor on `npm run lint` / `npm run typecheck`
  - current evidence points to a local host permission / file-lock condition, not a repo config defect

## Failures

- GitHub-hosted workflow was not rerun from this sandbox, so there is not yet a fresh remote green run attached to this report
- Local `npm ci --workspaces --include-workspace-root` is blocked by host `EPERM`, so the exact new workflow install step is not fully reverified on this workstation

## Risk assessment

- Low risk: the code change is tightly scoped to typecheck tooling and does not alter product behavior
- Low risk: repo-local `pyright` removes a workstation-specific hidden dependency that was already breaking CI
- Medium risk: until the branch is pushed and GitHub reruns checks, the final mergeability is inferred from local evidence rather than verified remotely
- Medium risk: the Python job now depends on Node installation in the runner, but this is explicit and versioned in the workflow rather than implicit in a user profile

## Recommendation

`merge_with_known_risks`

Reason:
- the root cause is confirmed and the replacement path passes locally
- one remote rerun is still required before the branch can be called fully `ready_to_merge`

## Follow-up items

- push this branch so PR-001 picks up the workflow and `pyright` changes
- rerun the PR checks and confirm the `python` job turns green on GitHub-hosted Windows
- if `npm ci --workspaces --include-workspace-root` fails on GitHub as well, capture the exact runner log before changing install flags or script behavior
