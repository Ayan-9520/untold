"""Abstract storyboard AI provider."""

from abc import ABC, abstractmethod

from app.domain.storyboard.types import StoryboardAgentRequest, StoryboardAgentResult


class StoryboardProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: StoryboardAgentRequest) -> StoryboardAgentResult:
        ...
