# Monorepo Skeleton Validation

## Scope

PR-001 validates the AERIS monorepo skeleton on branch `codex/p1-monorepo-skeleton-validation` without implementing product features. The goal is to keep the repository installable, importable, and testable across Python, Node, Rust, and Docker-facing tooling.

## What Was Fixed

1. Added [`tests/conftest.py`](/C:/Repos/active/ai-agent/AI-Flight-Recorder/tests/conftest.py) to insert the repository root into `sys.path` during pytest startup.
2. Verified the requested Python imports under `uv run python`:
   - `from apps.api.app.main import app`
   - `from packages.schema.flight_recorder_schema import ...`
   - `from packages.testkit import ...`
3. Confirmed the skeleton surfaces under `apps/`, `packages/`, `workers/`, `tests/`, `edge/`, and `infra/` are present and exercised by unit, integration, smoke, and e2e checks.

## Commands Run

All Python commands below were run with standard Windows environment variables set in-shell:
`SystemRoot=C:\Windows`, `windir=C:\Windows`, `TEMP=C:\Windows\Temp`, `TMP=C:\Windows\Temp`, `ComSpec=C:\Windows\System32\cmd.exe`.

Requested commands:

```powershell
uv sync --group dev
uv run ruff check .
uv run python -m pytest tests/unit -q
uv run python -m pytest tests/smoke -q
npm run lint --if-present
npm run typecheck --if-present
cargo check --manifest-path edge/daemon/Cargo.toml
docker compose -f infra/compose/docker-compose.yml config
```

Additional checks for repo clarity:

```powershell
uv run python -c "from apps.api.app.main import app; from packages.schema.flight_recorder_schema import HealthStatus; from packages.testkit import load_trace_bundle_fixture; print(app.title, HealthStatus.__name__, load_trace_bundle_fixture().__class__.__name__)"
uv run pytest tests/unit -q
uv run pytest tests/smoke -q
uv run python -m pytest tests/integration -q
uv run python -m pytest tests/e2e -q
docker --version
docker compose version
docker-compose --version
docker-compose -f infra/compose/docker-compose.yml config
```

## Passing Commands

- `uv sync --group dev`
- `uv run ruff check .`
- `uv run python -m pytest tests/unit -q`
- `uv run python -m pytest tests/smoke -q`
- `npm run lint --if-present`
- `npm run typecheck --if-present`
- `cargo check --manifest-path edge/daemon/Cargo.toml`
- `uv run pytest tests/unit -q`
- `uv run pytest tests/smoke -q`
- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/e2e -q`
- `uv run python -c "...requested imports..."`
- `docker-compose -f infra/compose/docker-compose.yml config`

## Failing Commands

- `docker compose -f infra/compose/docker-compose.yml config`
  - Result: failed immediately with `docker: unknown command: docker compose`
  - Cause: the host provides classic `docker-compose` v5.1.1, but not the Docker Compose v2 subcommand requested for this PR
  - Repo impact: `infra/compose/docker-compose.yml` itself is valid, confirmed by successful `docker-compose -f infra/compose/docker-compose.yml config`

## Existing Test Status

- Unit tests: passing
- Integration tests: passing
- Smoke tests: passing
- E2E tests: passing
- No existing test files remain in a failing-but-undocumented state after the pytest path bootstrap fix

## Risks

1. The validation host is missing the `docker compose` v2 CLI path expected by the requested command.
2. The current environment cannot fetch from GitHub, so the branch was created from the local `origin/master` reference rather than a freshly fetched remote tip.
3. Python validation in this Codex shell depends on restoring standard Windows environment variables before invoking `uv run ...`; this is a host-shell condition, not a repository code defect.

## Follow-up Tasks

1. Install or enable Docker Compose v2 so `docker compose -f infra/compose/docker-compose.yml config` can pass exactly as written.
2. Restore outbound network/DNS access before pushing the branch or opening a Draft PR.
3. Keep using the repo-root pytest bootstrap when adding new Python packages under `apps/`, `packages/`, or `workers/`, so plain `pytest` continues to resolve top-level imports.
