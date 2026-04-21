# `packages/schema`

此 package 保存兩種東西：

- Python typed models：位於 `flight_recorder_schema/`
- raw SQL migrations：位於 `migrations/`

目前第一版 migration 為：

- `migrations/0001_canonical_schema.up.sql`
- `migrations/0001_canonical_schema.down.sql`

它實作的範圍是 guide seed-4 指向的 canonical observability entities：

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

手動套用方式範例：

```bash
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.up.sql
psql "$DATABASE_URL" -f packages/schema/migrations/0001_canonical_schema.down.sql
```

