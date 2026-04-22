# AERIS Flight Recorder

Monorepo bootstrap for an **AI / Agent / LLM observability platform** focused on execution history, provenance, evidence grading, and replay-friendly explanations.

## Current state

This repository now contains a runnable local MVP baseline aligned to
`COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`:

- `apps/api`
  FastAPI surfaces for ingest, query, replay, research, and governance, with
  repository auto-selection between fixture mode and live Postgres mode.
- `apps/web`
  Next.js App Router pages that prefer live API reads and fall back to fixture data
  when the API is unavailable. The `/research` page also exposes the Drive connector
  acceptance surface for auth status, sync receipts, change tracking, and activity data.
- `packages/schema`
  Canonical schema models plus Postgres migration slices for core observability entities,
  governance surfaces, cognitive-state surfaces, research ingestion, replay verification,
  and Drive activity persistence.
- `packages/edge_sdk`
  Minimal Python edge/emitter SDK for the normalized ingest demo path.
- `scripts/bootstrap_local.py`
  Applies migrations and seeds demo data into a local Postgres instance.
- `scripts/emit_demo_trace.py`
  Posts a demo normalized trace bundle into the ingest API.
- `infra/compose/docker-compose.yml`
  Local single-machine baseline for `api`, `web`, `postgres`, `redis`, `minio`,
  `otel-collector`, and `edge-daemon`.

## System of record

Read these files in order before doing non-trivial work:

1. `AGENTS.md`
2. `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`
3. `.agent/PLANS.md`
4. the newest relevant file in `plans/active/`
5. supporting docs in `docs/`

## Repository layout

```text
.
├─ apps/
│  ├─ api/
│  └─ web/
├─ packages/
│  ├─ schema/
│  ├─ testkit/
│  └─ ui/
├─ workers/
│  ├─ ingest/
│  ├─ drive_sync/
│  ├─ arxiv_sync/
│  └─ replay/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ smoke/
├─ docs/
├─ plans/
└─ reports/
```

## Developer contract

Root `Makefile` defines the canonical task names required by the repo contract:

- `make setup`
- `make lint`
- `make typecheck`
- `make unit`
- `make integration`
- `make smoke`
- `make test`
- `make validate`

If `make` is unavailable on your platform, run the underlying commands directly:

```bash
uv sync --group dev
npm install --workspaces --include-workspace-root
uv run ruff check .
uv run mypy apps packages workers tests
uv run pytest tests/unit -q
uv run pytest tests/integration -q
uv run pytest tests/smoke -q
npm run lint --workspace @aeris/web
npm run typecheck --workspace @aeris/web
```

## Local MVP bring-up

When `make` is not available, run the underlying commands directly.

1. Install local dependencies.

```bash
uv sync --group dev
npm install --workspaces --include-workspace-root
```

2. Validate the compose baseline.

```bash
docker-compose -f infra/compose/docker-compose.yml config
```

3. Start the local stack.

```bash
docker-compose -f infra/compose/docker-compose.yml up --build
```

The `api` container is configured with:

- `AERIS_AUTO_BOOTSTRAP=true`
- `AERIS_SEED_DEMO=true`
- `AERIS_REPOSITORY_BACKEND=postgres`

So it will wait for Postgres, apply migrations, materialize demo blob artifacts, and
seed the demo trace during startup.

4. Optional local commands outside Docker.

```bash
uv run python scripts/bootstrap_local.py
uv run python scripts/emit_demo_trace.py
```

These commands require a reachable Postgres instance on `DATABASE_URL`.

## Migrations

The first Postgres canonical migration lives in:

- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`

These migrations cover:

- `sessions`
- `traces`
- `steps`
- `observations`
- `state_deltas`
- `artifacts`
- `evidence_edges`
- `claims`
- `explanation_records`
- `evaluations`
- `interventions`
- `audit_events`
- `policy_rules`
- `retention_policies`

They intentionally do not yet include `spans` or research-ingestion tables.

The current migration slices are:

- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0002_governance_surfaces.up.sql`
- `packages/schema/migrations/0003_cognitive_state_surfaces.up.sql`
- `packages/schema/migrations/0004_research_ingestion_surfaces.up.sql`
- `packages/schema/migrations/0005_replay_verification_surfaces.up.sql`
- `packages/schema/migrations/0006_drive_activity_surfaces.up.sql`

Selected later slices add:

- `tasks`
- `plan_versions`
- `state_snapshots`
- `traces.task_id` foreign key wiring
- `research_documents`
- `research_sync_runs`
- `research_sync_cursors`
- `replay_runs`
- `verification_records`
- `research_drive_activity_events`

## Notes

- `.agents/skills/` and `.codex/` are workflow infrastructure. Do not modify them unless the task explicitly targets that infrastructure.
- Validation evidence for major work belongs in `reports/validation/`.
- Move completed plans from `plans/active/` to `plans/done/` only after validation passes.
