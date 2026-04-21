# `packages/edge_sdk`

最小 Python Edge SDK / emitter API。這一版先提供：

- `AerisEdgeClient`
- `build_demo_request()`

用途是讓本地 demo 能走「sample emitter -> normalized ingest API」這條 live path，而不是只靠 fixture repository。
