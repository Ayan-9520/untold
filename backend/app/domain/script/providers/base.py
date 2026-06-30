"""Abstract script AI provider."""

from abc import ABC, abstractmethod

from app.domain.script.types import ScriptAgentRequest, ScriptAgentResult


class ScriptProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def write(self, request: ScriptAgentRequest) -> ScriptAgentResult:
        ...
