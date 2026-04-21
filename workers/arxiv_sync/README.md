# `workers/arxiv_sync`

目前已提供 `job.py` fixture entrypoint，對應 metadata-only arXiv search contract。

目前 `job.py` 會回傳 research sync receipt，包含：

- `sync_run_id`
- `query`
- `cursor`
- `item_count`

後續可在這裡擴充：

- 即時查詢
- paging
- polite delay
- OAI-PMH metadata harvest
