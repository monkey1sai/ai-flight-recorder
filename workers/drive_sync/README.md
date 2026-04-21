# `workers/drive_sync`

目前已提供 `job.py` fixture entrypoint，對應 read-only Drive search contract。

目前 `job.py` 會回傳 research sync receipt，包含：

- `sync_run_id`
- `query`
- `cursor`
- `item_count`

後續可在這裡擴充：

- Google Drive 搜尋
- change tracking
- Docs export
- Drive Activity enrichment
