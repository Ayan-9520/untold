"""Search provider stub — swap for Google, Bing, SerpAPI, etc."""

from app.domain.research.providers.base import ResearchProvider
from app.domain.research.types import ResearchAgentRequest, ResearchAgentResult


class SearchStubProvider(ResearchProvider):
    id = "search_stub"
    label = "Web Search (configure API key)"

    def is_available(self) -> bool:
        return False

    def research(self, request: ResearchAgentRequest) -> ResearchAgentResult:
        return ResearchAgentResult(
            summary="Search provider not configured. Set SEARCH_API_KEY to enable web retrieval.",
            provider=self.id,
        )
