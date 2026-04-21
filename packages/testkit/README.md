# `packages/testkit`

這個 package 提供可重用的 fixture 與 loader，讓 API、workers、web mock adapter、integration tests 與 e2e tests 可以吃同一批 sample data，而不是各自維護不同版本的 trace 形狀。

目前包含：

- `fixtures/demo_trace_bundle.json`
- `fixtures/drive_search_results.json`
- `fixtures/arxiv_search_results.json`
- `fixture_loader.py`
