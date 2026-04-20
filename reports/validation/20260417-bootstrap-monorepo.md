# Validation Report: Bootstrap Monorepo Skeleton

Date: 2026-04-17
Plan: `plans/active/20260417-bootstrap-monorepo.md`

## Scope

Validate the bootstrap slice end to end:

- root manifests and `Makefile`
- minimal FastAPI API surface
- minimal Next.js shell
- schema package
- Python unit / integration / smoke coverage
- local dependency installation path for Python and Node

## Environment notes

- This Codex Windows shell initially lacked `TEMP`, `TMP`, `SystemRoot`, `windir`, and `ComSpec`.
- Python commands were executed with those variables set explicitly so `uv`, `pytest`, and `asyncio.windows_events` could run correctly.
- npm commands were executed by prepending `tools/bin` to `PATH`, which forces the repo-local `npm.cmd` / `npm.ps1` wrapper and uses the repo-local `.npmrc` cache configuration.
- Python dependencies were resolved from repo-local vendor artifacts in `vendor/python/wheels/`; Node dependency installation also relies on `vendor/npm/brace-expansion-1.1.14.tgz`.

## Commands

- `uv lock --offline --no-index --find-links .\vendor\python\wheels --upgrade-package mypy`
- `uv sync --group dev --offline`
- `npm install --workspaces --include-workspace-root --offline`
- `uv run ruff check .`
- `uv run mypy apps packages workers tests`
- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/smoke -q`
- `npm run lint --workspace @aeris/web`
- `npm run typecheck --workspace @aeris/web`
- `python -m compileall apps packages workers tests`
- inline Python repo-contract check for required paths and `Makefile` targets

## Results

Passed
- `uv lock --offline --no-index --find-links .\vendor\python\wheels --upgrade-package mypy`
  Result: resolved and refreshed the lockfile against the repo-local wheelhouse.
- `uv sync --group dev --offline`
  Result: succeeded; environment is synchronized from local wheel artifacts.
- `npm install --workspaces --include-workspace-root --offline`
  Result: succeeded via repo-local npm wrapper and offline cache.
- `uv run ruff check .`
  Result: `All checks passed!`
- `uv run mypy apps packages workers tests`
  Result: `0 errors, 0 warnings, 0 informations`
- `uv run python -m pytest tests/unit -q`
  Result: `4 passed`
- `uv run python -m pytest tests/integration -q`
  Result: `5 passed`
- `uv run python -m pytest tests/smoke -q`
  Result: `4 passed`
- `npm run lint --workspace @aeris/web`
  Result: completed successfully with no remaining warnings.
- `npm run typecheck --workspace @aeris/web`
  Result: completed successfully.
- `python -m compileall apps packages workers tests`
  Result: all Python files in `apps/`, `packages/`, `workers/`, and `tests/` compiled successfully.
- inline Python repo-contract check
  Result: `bootstrap contract ok`

## Remaining notes

- `make` is still not installed in the current Windows shell, so validation was executed through the underlying commands instead of direct `make <target>` invocations.
- The bootstrap web slice is still validated only by lint + typecheck. Browser automation and UI e2e coverage remain out of scope for this plan.

## Conclusion

This is a full validation report for the bootstrap plan, not a partial report.

The bootstrap monorepo skeleton now has:

- reproducible offline Python setup through `uv.lock` and `vendor/python/wheels/`
- reproducible offline npm setup through `tools/bin/npm.*`, `.npmrc`, `package-lock.json`, and `vendor/npm/brace-expansion-1.1.14.tgz`
- passing Python tests, lint, typecheck, compile checks, and web lint/typecheck
