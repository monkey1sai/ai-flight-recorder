from __future__ import annotations

import json
from pathlib import Path

from packages.schema.flight_recorder_schema import ResearchSearchResponse, TraceBundleView

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures"


def fixture_path(name: str) -> Path:
    return FIXTURE_ROOT / name


def _load_fixture(name: str) -> dict[str, object]:
    return json.loads(fixture_path(name).read_text(encoding="utf-8"))


def load_trace_bundle_fixture() -> TraceBundleView:
    return TraceBundleView.model_validate(_load_fixture("demo_trace_bundle.json"))


def load_drive_search_fixture() -> ResearchSearchResponse:
    return ResearchSearchResponse.model_validate(_load_fixture("drive_search_results.json"))


def load_arxiv_search_fixture() -> ResearchSearchResponse:
    return ResearchSearchResponse.model_validate(_load_fixture("arxiv_search_results.json"))
