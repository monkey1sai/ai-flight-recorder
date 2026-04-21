# postgres-migrations

## summary

Added the first canonical Postgres migration slice as a small, migration-only PR from `master`: raw SQL up/down migrations, a minimal typed schema package, targeted tests, an architecture note, and validation evidence.

## changed files

- `.gitignore`
- `plans/active/20260421-canonical-schema-migrations.md`
- `pyproject.toml`
- `packages/__init__.py`
- `packages/schema/__init__.py`
- `packages/schema/README.md`
- `packages/schema/flight_recorder_schema/__init__.py`
- `packages/schema/flight_recorder_schema/canonical.py`
- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`
- `tests/conftest.py`
- `tests/unit/test_canonical_models_contract.py`
- `tests/integration/test_canonical_migration_spec.py`
- `docs/architecture/canonical-schema.md`
- `reports/validation/20260421-canonical-schema-migrations.md`
- `reports/codex/postgres-migrations.md`

## validation commands

- `uv run ruff check .`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/unit/test_canonical_models_contract.py -q -p no:cacheprovider`
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/integration/test_canonical_migration_spec.py -q -p no:cacheprovider`

## pass/fail results

- `uv run ruff check .`: pass
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/unit/test_canonical_models_contract.py -q -p no:cacheprovider`: pass (`1 passed`)
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run python -m pytest tests/integration/test_canonical_migration_spec.py -q -p no:cacheprovider`: pass (`2 passed`)
- `uv sync --group dev`: fail in this worktree due Windows access-denied while writing `.venv`, but not required to complete the targeted checks

## known limitations

- No live Postgres runtime verification.
- This branch intentionally excludes the broader monorepo bootstrap and only carries the migration slice.
- Tooling emitted cache/temp access warnings in this Windows worktree.

## follow-up tasks

- Run the migration on a real Postgres instance.
- Add follow-up migrations for broader operational tables.
