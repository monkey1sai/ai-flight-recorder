from .admin import router as admin_router
from .ingest import router as ingest_router
from .query import router as query_router
from .replay import router as replay_router
from .research import router as research_router

__all__ = [
    "admin_router",
    "ingest_router",
    "query_router",
    "replay_router",
    "research_router",
]
