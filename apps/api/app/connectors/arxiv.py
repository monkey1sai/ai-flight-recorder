from __future__ import annotations

from packages.schema.flight_recorder_schema import ResearchSearchResponse
from packages.testkit import load_arxiv_search_fixture


class FixtureArxivConnector:
    def __init__(self) -> None:
        self.seed = load_arxiv_search_fixture()

    def search(self, query: str) -> ResearchSearchResponse:
        tokens = [token.strip().lower() for token in query.split() if token.strip()]

        if not tokens:
            return self.seed.model_copy(deep=True)

        matches = []
        for item in self.seed.items:
            haystack = " ".join([item.title, item.summary, *item.tags]).lower()
            if all(token in haystack for token in tokens):
                cloned = item.model_copy(deep=True)
                cloned.provenance.query = query
                matches.append(cloned)

        return ResearchSearchResponse(query=query, items=matches)
