from fastapi import FastAPI

from apps.api.app.routers import (
    admin_router,
    ingest_router,
    query_router,
    replay_router,
    research_router,
)
from packages.schema.flight_recorder_schema import EvidenceGrade, HealthStatus

app = FastAPI(
    title="AERIS Flight Recorder API",
    version="0.1.0",
    summary=(
        "Fixture-backed observability API surface for ingest, query, replay, research, "
        "and governance."
    ),
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(replay_router)
app.include_router(research_router)
app.include_router(admin_router)


@app.get("/", tags=["meta"])
def root() -> dict[str, object]:
    return {
        "service": "AERIS Flight Recorder API",
        "status": "operator-slice",
        "evidence_grades": [grade.value for grade in EvidenceGrade],
        "surfaces": [
            "ingest",
            "query",
            "replay",
            "research",
            "admin",
        ],
    }


@app.get("/healthz", response_model=HealthStatus, tags=["ops"])
def healthz() -> HealthStatus:
    return HealthStatus()
