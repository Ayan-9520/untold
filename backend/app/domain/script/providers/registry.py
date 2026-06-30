"""Script writer provider registry."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.domain.script.providers.base import ScriptProvider
from app.domain.script.providers.demo import DemoScriptProvider
from app.domain.script.providers.llm_bridge import LLMScriptProvider
from app.domain.script.types import ScriptAgentRequest, ScriptAgentResult

logger = logging.getLogger("untold.script.registry")


class ScriptProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ScriptProvider] = {}

    def register(self, provider: ScriptProvider) -> None:
        self._providers[provider.id] = provider

    def list_providers(self) -> list[dict]:
        return [{"id": p.id, "label": p.label, "available": p.is_available()} for p in self._providers.values()]

    def resolve(self, preferred: str | None = None) -> ScriptProvider:
        settings = get_settings()
        order: list[str] = []
        if preferred:
            order.append(preferred)
        order.append(getattr(settings, "script_default_provider", "demo"))
        order.extend(["llm", "demo"])

        seen: set[str] = set()
        for pid in order:
            if pid in seen:
                continue
            seen.add(pid)
            p = self._providers.get(pid)
            if p and p.is_available():
                return p
        demo = self._providers.get("demo")
        if demo:
            return demo
        raise RuntimeError("No script provider available")

    def write(self, request: ScriptAgentRequest, provider_id: str | None = None) -> ScriptAgentResult:
        provider = self.resolve(provider_id)
        result = provider.write(request)
        result.provider = provider.id
        return result


_registry: ScriptProviderRegistry | None = None


def get_script_registry() -> ScriptProviderRegistry:
    global _registry
    if _registry is None:
        _registry = ScriptProviderRegistry()
        _registry.register(DemoScriptProvider())
        _registry.register(LLMScriptProvider())
    return _registry
