# AERIS Flight Recorder

Monorepo bootstrap for an **AI / Agent / LLM observability platform** focused on execution history, provenance, evidence grading, and replay-friendly explanations.

## Current state

This repository is no longer just a docs kit. It now contains the first bootstrap skeleton aligned to `COMPLETE_CODEX_PROJECT_GUIDE_zh-TW.md`:

- `apps/api`
  Minimal FastAPI surface with `/healthz` and bootstrap metadata.
- `apps/web`
  Next.js App Router shell that makes the evidence-grade contract visible from day one.
- `packages/schema`
  Typed Python boundary for evidence grades plus the first canonical Postgres migration pair.
- `workers/*`
  Reserved locations for ingest, Drive sync, arXiv sync, and replay workers.
- `tests/*`
  Unit, integration, and smoke tests that verify the first runnable slice and repo contract.
- `plans/active/20260417-bootstrap-monorepo.md`
  The active ExecPlan that defines the current bootstrap milestone.
- `plans/active/20260417-canonical-schema-migrations.md`
  The schema/migration ExecPlan for the first Postgres canonical model slice.

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

## Immediate next milestones

1. Build the canonical observability schema beyond the bootstrap envelope.
2. Implement the ingestion API with persistence.
3. Replace the web shell placeholders with timeline, run detail, and evidence panel slices.
4. Add Google Drive and arXiv connectors with provenance retention.

## Migrations

The first Postgres canonical migration lives in:

- `packages/schema/migrations/0001_canonical_schema.up.sql`
- `packages/schema/migrations/0001_canonical_schema.down.sql`

This migration covers:

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

It intentionally does not yet include `spans`, `tasks`, `plan_versions`, or research-ingestion tables.

## Notes

- `.agents/skills/` and `.codex/` are workflow infrastructure. Do not modify them unless the task explicitly targets that infrastructure.
- Validation evidence for major work belongs in `reports/validation/`.
- Move completed plans from `plans/active/` to `plans/done/` only after validation passes.
