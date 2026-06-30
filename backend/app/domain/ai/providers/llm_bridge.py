"""Bridge unified LLM providers into the legacy AIProvider registry."""

from __future__ import annotations

from app.ai.providers.base import LLMProvider
from app.domain.ai.providers.base import AIProvider
from app.domain.ai.types import AIJobRequest, AIJobResult


class LLMProviderBridge(AIProvider):
    """Adapts app.ai.providers LLMProvider to domain AIProvider."""

    def __init__(self, inner: LLMProvider) -> None:
        self._inner = inner
        self.id = inner.id
        self.label = inner.label
        self.supports_modules = getattr(inner, "supports_modules", frozenset())

    def is_available(self) -> bool:
        return self._inner.is_available()

    def supports(self, module: str) -> bool:
        if hasattr(self._inner, "supports"):
            return self._inner.supports(module)
        return not self.supports_modules or module in self.supports_modules

    def generate(self, request: AIJobRequest) -> AIJobResult:
        out = self._inner.complete(
            module=request.module,
            prompt=request.prompt,
            parameters=request.parameters,
        )
        return AIJobResult(
            output_text=out.get("output_text", ""),
            result_url=out.get("result_url"),
            meta=out.get("meta") or {},
            provider=self.id,
        )
