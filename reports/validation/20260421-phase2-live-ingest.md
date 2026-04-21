# Validation Report: Phase 2 Live Ingest

## Scope

Validate the Phase 2 live ingest/data-layer slice:

- repository auto-selection between fixture mode and Postgres mode
- normalized ingest path with blob materialization
- local bootstrap/runtime settings and demo ingest script
- edge demo client posting a normalized trace bundle into the live API

## Commands run

```powershell
docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/ruff.exe check apps/api/app packages/schema packages/edge_sdk scripts
docker-compose -f infra/compose/docker-compose.yml up --build -d
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe -m pytest tests/integration/test_api_operator_surfaces.py -q
Invoke-WebRequest http://localhost:8080/healthz
C:/Repos/active/ai-agent/AI-Flight-Recorder/.venv/Scripts/python.exe scripts/emit_demo_trace.py
Invoke-WebRequest http://localhost:8080/api/v1/traces/22222222-2222-4222-8222-222222222222
```

## Results

- `ruff`
  Passed.
- `docker-compose down -v --remove-orphans`
  Passed. Existing compose volumes and containers were removed before validation.
- `docker-compose up --build -d`
  Passed. `api`, `web`, `postgres`, `redis`, `minio`, and `otel-collector` all started.
- `pytest tests/integration/test_api_operator_surfaces.py -q`
  Passed. `2 passed`.
- `GET /healthz`
  Passed with HTTP `200`.
- `python scripts/emit_demo_trace.py`
  Passed. Returned `ingested trace_id=22222222-2222-4222-8222-222222222222`.
- `GET /api/v1/traces/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200`.

## Failures

- None in the validated Phase 2 scope.

## Risk assessment

- Medium scope risk: the current data layer already carries some internal forward-compatible structures used by later phases, but this PR only validates the live ingest/runtime path.
- Low runtime risk: the normalized ingest and Postgres write path are proven by compose-backed validation.

## Recommendation

`ready_to_merge`

## Follow-up items

- Product Phase 4 and Phase 5 should expose cognitive/why surfaces explicitly in later PRs instead of expanding this PR further.
