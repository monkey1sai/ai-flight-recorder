# Canonical Schema Migration Notes

## Purpose

`packages/schema/migrations/0001_canonical_schema.up.sql` 是第一版 Postgres canonical schema migration。它的工作不是把整個平台一次建完，而是先固定住 guide 與 `總覽.md` 中最核心的 observability entities。

## Why raw SQL first

- repo 目前還沒有穩定的 migration runtime
- raw SQL 最容易 review、最不依賴特定工具
- 後續無論採 Alembic、dbmate 或其他工具，都可以把這批 SQL 視為 source of truth

## Implemented tables

- `sessions`
- `traces`
- `steps`
- `artifacts`
- `observations`
- `state_deltas`
- `claims`
- `evidence_edges`
- `explanation_records`
- `evaluations`
- `interventions`

## Deliberate omissions

這一版刻意不含：

- `spans`
- `tasks`
- `plan_versions`
- `state_snapshots`
- `counterfactual_runs`
- research-ingestion specific tables

原因是本輪任務直接對齊 `docs/TASK_SEEDS.md` 的 canonical schema seed，先把 MVP 需要的證據與解釋實體固定下來，再逐步擴充營運層表。

## Design rules encoded in the migration

- append-only by default: only `created_at`，不設 `updated_at`
- raw payload boundaries: DB 只留 `storage_ref` / `content_ref` / JSONB metadata
- graph boundary: `evidence_edges` 使用 relation table，而不是 graph DB 專屬結構
- explanation grades: `evidence_grade` enum 固定 `observed / self_reported / inferred / verified`
- unsupported claims: `claims.verification_status` 內建 `unsupported`

## Manual application

```bash
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.up.sql
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.down.sql
```

## Expected follow-up

1. 用真實 Postgres instance 跑 up/down migration smoke
2. 新增 `spans`, `tasks`, `plan_versions`, `state_snapshots`
3. 把 ingest API 與 repositories 接到這批表
4. 補 migration runner / CI integration

