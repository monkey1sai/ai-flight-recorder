# Google Drive Live Connector Research Note

## Question

What exact Google API behaviors, scopes, limits, and provenance fields must this repository implement to safely replace the fixture Drive connector with a live connector?

## Why this matters

This repo already has research persistence and API/UI surfaces. The missing work is live Google integration. The implementation must use current official behavior instead of memory so the connector, sync flows, and acceptance checklist stay correct.

## Source table

| Source | Retrieved | Why it matters |
| --- | --- | --- |
| Google Drive API changes guide | 2026-04-22 | Confirms `getStartPageToken` + `changes.list` flow and optional `changes.watch` behavior |
| Google Drive downloads/export guide | 2026-04-22 | Confirms `files.export` behavior and 10 MB export limit |
| Google Docs API `documents.get` reference | 2026-04-22 | Confirms Docs JSON retrieval and readonly scope |
| Google Docs auth guide | 2026-04-22 | Confirms `documents.readonly` scope |
| Google Drive Activity API request/reference docs | 2026-04-22 | Confirms `activity.query`, `itemName=items/{ITEM_ID}`, and readonly scope |
| Google Drive scopes guide | 2026-04-22 | Confirms available readonly scopes and scope narrowing guidance |

## Key facts

- Drive change tracking can be implemented with:
  - `changes.getStartPageToken`
  - `changes.list`
- `changes.watch` exists, but it is not required for a valid incremental sync flow.
- Google Workspace document export through `files.export` is limited to 10 MB.
- Google Docs content can be retrieved as structured JSON through `documents.get`.
- Drive Activity API v2 uses `POST /v2/activity:query`.
- Per-item activity requests use `itemName = "items/{ITEM_ID}"`.
- Relevant readonly scopes for this phase are:
  - `https://www.googleapis.com/auth/drive.readonly`
  - `https://www.googleapis.com/auth/documents.readonly`
  - `https://www.googleapis.com/auth/drive.activity.readonly`
- Provenance fields already modeled by this repo remain necessary for live Drive:
  - `source_id`
  - `source_uri`
  - `retrieved_at`
  - `query`
  - `cursor`
  - `checksum`
  - `export_status`

## Implementation consequences

- This phase can stay bounded by implementing pull-based change tracking only.
- `files.export` failures caused by size or format must not fail the whole sync.
- Docs JSON and export bytes should go to blob storage; tables should only store refs and metadata.
- Drive Activity persistence should be a dedicated table rather than being hidden in sync-run metadata.
- The live connector must expose auth status separately so `/research` can distinguish:
  - live + authorized
  - live + blocked
  - auto + fixture fallback

## Open questions

- None blocking after product decisions were fixed in the active ExecPlan.

## Next safe action

Implement settings/env, connector selection, and auth-status surfaces first before wiring search/sync/activity persistence.
