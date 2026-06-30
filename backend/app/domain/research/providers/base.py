"""Abstract research agent provider — LLM or search backends."""

from abc import ABC, abstractmethod

from app.domain.research.types import ResearchAgentRequest, ResearchAgentResult


class ResearchProvider(ABC):
    id: str = "base"
    label: str = "Base Research Provider"

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def research(self, request: ResearchAgentRequest) -> ResearchAgentResult:
        ...
