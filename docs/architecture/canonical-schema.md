# Canonical Schema Migration Notes

## Purpose

`packages/schema/migrations/0001_canonical_schema.up.sql` 是第一版 Postgres canonical schema migration。它的目標是把 guide 中最核心的 observability entities 固定成可 review、可持續擴充的資料邊界。

## Why raw SQL first

- repo 目前沒有既定 migration runtime
- raw SQL 最容易 review
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

原因是本輪只先固定 canonical schema 的第一個 durable slice。

## Design rules encoded in the migration

- append-only by default：只設 `created_at`，不設 `updated_at`
- raw payload boundaries：DB 只留 `storage_ref` / `content_ref` / JSONB metadata
- graph boundary：`evidence_edges` 先用 relation table
- explanation grades：`evidence_grade` enum 固定 `observed / self_reported / inferred / verified`
- unsupported claims：`claims.verification_status` 內建 `unsupported`

## Manual application

```bash
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.up.sql
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.down.sql
```

## Expected follow-up

1. 用真實 Postgres instance 跑 up/down migration smoke
2. 新增 `spans`, `tasks`, `plan_versions`, `state_snapshots`
3. 把 ingest API / repository 接到這批表

