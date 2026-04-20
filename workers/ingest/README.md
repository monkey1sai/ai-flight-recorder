# `workers/ingest`

目前已提供 `job.py` fixture entrypoint，會把 shared trace bundle 送進 API 對應的 ingest service。

後續可在這裡擴充：

- trace normalization
- artifact ingest
- append-only event persistence
- queue-driven ingest orchestration
