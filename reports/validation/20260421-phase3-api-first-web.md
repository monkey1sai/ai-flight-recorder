# Validation Report: Phase 3 API-First Web

## Scope

Validate the Phase 3 API-first web slice:

- home, timeline, trace detail, replay, research, and admin pages prefer live API reads
- fixture data remains fallback only
- operator-facing Web routes remain renderable after the API-first client is introduced

## Commands run

```powershell
docker-compose -f infra/compose/docker-compose.yml down -v --remove-orphans
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
docker-compose -f infra/compose/docker-compose.yml up --build -d
Invoke-WebRequest http://localhost:3000/
Invoke-WebRequest http://localhost:3000/timeline
Invoke-WebRequest http://localhost:3000/traces/22222222-2222-4222-8222-222222222222
Invoke-WebRequest http://localhost:3000/replay/22222222-2222-4222-8222-222222222222
Invoke-WebRequest http://localhost:3000/research
Invoke-WebRequest http://localhost:3000/admin
```

## Results

- `docker-compose down -v --remove-orphans`
  Passed.
- `npm run lint --workspace @aeris/web`
  Passed.
- `npm run typecheck --workspace @aeris/web`
  Passed.
- `docker-compose up --build -d`
  Passed.
- `GET /`
  Passed with HTTP `200`.
- `GET /timeline`
  Passed with HTTP `200`.
- `GET /traces/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200`.
- `GET /replay/22222222-2222-4222-8222-222222222222`
  Passed with HTTP `200`.
- `GET /research`
  Passed with HTTP `200`.
- `GET /admin`
  Passed with HTTP `200`.

## Failures

- None in the validated Phase 3 scope.

## Risk assessment

- Low risk: this PR is read-path focused and does not reopen the persistence layer.
- Medium risk: trace detail intentionally excludes the cognitive task/plan panels until a later PR exposes those surfaces explicitly.

## Recommendation

`ready_to_merge`

## Follow-up items

- Expose cognitive task/plan UI in the next PR rather than expanding this API-first surface further.
