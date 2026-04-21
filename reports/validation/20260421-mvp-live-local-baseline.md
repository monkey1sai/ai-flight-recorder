# Validation Report: MVP Live Local Baseline Runnable Checkpoint

## Scope

Validate the new live local baseline and API-first operator slice for:

- repository auto-selection between fixture mode and Postgres mode
- normalized ingest path with blob materialization
- local bootstrap scripts and compose baseline
- API-first web data adapter for timeline / trace detail / replay / research / admin
- governance migration slice
- minimal Python edge SDK demo path
- actual compose bring-up, demo ingest, API reachability, and Web route reachability

## Commands run

```powershell
uv run python -m pytest tests/unit -q
uv run python -m pytest tests/integration -q
uv run python -m pytest tests/e2e -q
uv run python -m pytest tests/smoke -q
uv run ruff check .
node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
cargo check --manifest-path edge/daemon/Cargo.toml
docker-compose -f infra/compose/docker-compose.yml config
docker-compose -f infra/compose/docker-compose.yml up --build -d
uv run python scripts/emit_demo_trace.py
Invoke-WebRequest http://localhost:8080/healthz | Select-Object -ExpandProperty Content
Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222 | Select-Object -ExpandProperty Content
(Invoke-WebRequest http://localhost:3000/).StatusCode
(Invoke-WebRequest http://localhost:3000/timeline).StatusCode
(Invoke-WebRequest http://localhost:3000/traces/22222222-2222-4222-8222-222222222222).StatusCode
(Invoke-WebRequest http://localhost:3000/replay/22222222-2222-4222-8222-222222222222).StatusCode
(Invoke-WebRequest http://localhost:3000/research).StatusCode
(Invoke-WebRequest http://localhost:3000/admin).StatusCode
uv run python scripts/bootstrap_local.py
```

## Results

- `uv run python -m pytest tests/unit -q`
  Passed.
- `uv run python -m pytest tests/integration -q`
  Passed. Includes the new normalized ingest test that materializes blob refs into a temp directory.
- `uv run python -m pytest tests/e2e -q`
  Passed.
- `uv run python -m pytest tests/smoke -q`
  Passed.
- `uv run ruff check .`
  Passed.
- `node ./node_modules/pyright/index.js -p pyrightconfig.json --level error apps packages workers tests`
  Passed.
- `npm run lint --workspace @aeris/web`
  Passed.
- `npm run typecheck --workspace @aeris/web`
  Passed.
- `cargo check --manifest-path edge/daemon/Cargo.toml`
  Passed.
- `docker-compose -f infra/compose/docker-compose.yml config`
  Passed. The local stack renders successfully with named volumes and API bootstrap env vars.
- `docker-compose -f infra/compose/docker-compose.yml up --build -d`
  Passed after fixing validation blockers in compose/runtime integration. Confirmed running services: `api`, `web`, `postgres`, `redis`, `minio`, `otel-collector`. The `edge-daemon` container currently exits `0` as a one-shot skeleton and is not counted as the runnable MVP proof.
- `uv run python scripts/emit_demo_trace.py`
  Passed. Returned `ingested trace_id=22222222-2222-4222-8222-222222222222 session_id=11111111-1111-4111-8111-111111111111`.
- `Invoke-WebRequest http://localhost:8080/healthz`
  Passed. Returned `{"status":"ok","service":"api","evidence_grades":["observed","self_reported","inferred","verified"]}`.
- `Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222`
  Passed. Returned a live trace bundle with canonical entities populated from Postgres, including `steps`, `observations`, `state_deltas`, `artifacts`, `claims`, `explanations`, `audit_events`, `policies`, and `retention`.
- `Invoke-WebRequest http://localhost:3000/`
  Passed with HTTP `200`.
- `Invoke-WebRequest http://localhost:3000/timeline`
  Passed with HTTP `200`.
- `Invoke-WebRequest http://localhost:3000/traces/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200` after rebuilding the web image with the Next 16 dynamic-route compatibility fix.
- `Invoke-WebRequest http://localhost:3000/replay/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200` after the same dynamic-route fix.
- `Invoke-WebRequest http://localhost:3000/research`
  Passed with HTTP `200`.
- `Invoke-WebRequest http://localhost:3000/admin`
  Passed with HTTP `200`.
- `uv run python scripts/bootstrap_local.py`
  Failed as expected without a running Postgres instance on `localhost:5432`. The script now resolves repo imports correctly and blocks only on missing infrastructure, not on Python path issues.

## Validation blockers fixed during this pass

- Compose used a non-existent MinIO release tag. Updated the image reference to a pullable tag.
- Docker build on Windows picked up host `node_modules` and failed. Added `.dockerignore` to keep the build context clean.
- The web image did not copy `vendor/npm`, so `npm install` could not resolve vendored tarballs.
- Publishing Postgres on host port `5432` conflicted with an existing local service. Internal-only services now stay on the compose network; only `api:8080` and `web:3000` are published.
- API ingest wrote `observations` before `artifacts`, which violated `observations.source_artifact_id` foreign keys. Persistence order now writes artifacts first.
- API bootstrap replayed SQL migrations on container restart and failed on already-existing enum types. Bootstrap now records/applies migrations idempotently.
- Next 16 requires async access to dynamic route `params`. `/traces/[id]` and `/replay/[id]` were updated and the web image was rebuilt so those pages return HTTP `200`.

## Blockers

- A reachable Postgres instance is still required to execute `scripts/bootstrap_local.py` outside Docker.
- OTel Collector still exports to `debug`; the live demo path currently uses normalized ingest instead of full OTLP protobuf ingestion.
- `edge-daemon` is still a one-shot skeleton and not yet part of the runnable MVP proof.

## Risk assessment

- The repository now has a real live persistence path and one successful compose bring-up proof in this shell.
- Research connectors remain fixture/mock-backed even though the UI now reads them through the live API surface.
- Replay and why panels now read live API data, but replay-backed verification logic is still limited to the existing bundle/explanation model.
- `make` is not available in this Windows PowerShell environment, so validation used the Makefile's underlying commands directly instead of claiming `make validate` was executed.

## Recommendation

- Treat this checkpoint as merge-ready for runnable validation / handoff of the current MVP baseline.
- Do not overclaim this as Phase 4 feature completion. It is a verified runnable checkpoint for the existing baseline plus the minimal fixes required to prove it.
- If the next phase starts, use this checkpoint as the handoff baseline and keep new work separate from local runtime validation.
