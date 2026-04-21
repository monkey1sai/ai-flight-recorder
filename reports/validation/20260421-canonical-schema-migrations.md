# Validation Report: Canonical Schema Postgres Migrations

Date: 2026-04-21
Plan: `plans/active/20260421-canonical-schema-migrations.md`

## Scope

Validate the first canonical schema migration slice:

- Postgres up/down migration SQL
- aligned Python typed models
- targeted migration tests
- migration architecture note

## Commands

- `uv run ruff check .`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/unit/test_canonical_models_contract.py -q -p no:cacheprovider`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/integration/test_canonical_migration_spec.py -q -p no:cacheprovider`
- future DB execution checks:
  - `psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.up.sql`
  - `psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.down.sql`

## Results

Passed
- `uv run ruff check .`
  Result: lint passed. Ruff emitted cache-write access warnings in this worktree, but no code issues remained after auto-fixing the `tests/conftest.py` import order.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/unit/test_canonical_models_contract.py -q -p no:cacheprovider`
  Result: `1 passed`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/integration/test_canonical_migration_spec.py -q -p no:cacheprovider`
  Result: `2 passed`

Blocked
- `uv sync --group dev`
  Result: failed while persisting `pluggy` metadata into `.venv` with Windows access-denied errors, even though subsequent `uv run ...` commands succeeded.
- `psql ...`
  Result: not executed because no live Postgres instance or migration runtime is configured in this task.

## Known gaps

- No live Postgres execution evidence yet.
- Broader operational tables such as `spans`, `tasks`, and `plan_versions` are intentionally deferred.
- Worktree-local cache/temp directories triggered Windows access warnings during tooling runs; they did not prevent the targeted checks from passing.
