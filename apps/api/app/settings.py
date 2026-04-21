from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    repository_backend: str = Field(default="auto")
    database_url: str = Field(default="postgresql://postgres:postgres@localhost:5432/aeris")
    blob_storage_root: Path = Field(default_factory=lambda: Path("tmp/blobstore"))
    api_base_url: str = Field(default="http://127.0.0.1:8080")
    auto_bootstrap: bool = Field(default=False)
    seed_demo_on_bootstrap: bool = Field(default=True)
    startup_db_timeout_seconds: int = Field(default=30, ge=1)


@lru_cache
def get_settings() -> AppSettings:
    import os

    return AppSettings(
        repository_backend=os.getenv("AERIS_REPOSITORY_BACKEND", "auto"),
        database_url=os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aeris"
        ),
        blob_storage_root=Path(os.getenv("BLOB_STORAGE_ROOT", "tmp/blobstore")),
        api_base_url=os.getenv("AERIS_API_BASE_URL", "http://127.0.0.1:8080"),
        auto_bootstrap=os.getenv("AERIS_AUTO_BOOTSTRAP", "false").lower() == "true",
        seed_demo_on_bootstrap=os.getenv("AERIS_SEED_DEMO", "true").lower() == "true",
        startup_db_timeout_seconds=int(os.getenv("AERIS_STARTUP_DB_TIMEOUT_SECONDS", "30")),
    )
