from packages.testkit import (
    load_arxiv_search_fixture,
    load_drive_search_fixture,
    load_trace_bundle_fixture,
)


def test_trace_bundle_fixture_exposes_operator_surfaces() -> None:
    bundle = load_trace_bundle_fixture()

    assert bundle.trace.trace_kind == "agent_run"
    assert len(bundle.steps) >= 4
    assert len(bundle.claims) >= 2
    assert len(bundle.policies) >= 2
    assert len(bundle.retention) >= 1


def test_research_fixtures_preserve_provenance() -> None:
    drive = load_drive_search_fixture()
    arxiv = load_arxiv_search_fixture()

    assert drive.items[0].provenance.source_type == "drive"
    assert drive.items[0].provenance.source_uri.startswith("https://drive.google.com/")
    assert arxiv.items[0].provenance.source_type == "arxiv"
    assert arxiv.items[0].provenance.source_uri.startswith("https://arxiv.org/abs/")
