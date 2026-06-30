"""Abstract AI provider interface."""

from abc import ABC, abstractmethod

from app.domain.ai.types import AIJobRequest, AIJobResult


class AIProvider(ABC):
    """Vendor-neutral AI backend. Implement for OpenAI, Anthropic, local models, etc."""

    id: str = "base"
    label: str = "Base Provider"
    supports_modules: frozenset[str] = frozenset()

    @abstractmethod
    def is_available(self) -> bool:
        """Return True when this provider can accept jobs (credentials configured, etc.)."""

    @abstractmethod
    def generate(self, request: AIJobRequest) -> AIJobResult:
        """Run generation synchronously. Called from Celery worker."""

    def supports(self, module: str) -> bool:
        return not self.supports_modules or module in self.supports_modules
