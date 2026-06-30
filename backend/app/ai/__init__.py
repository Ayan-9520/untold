"""UNTOLD unified AI layer."""

from app.ai.config import AIConfig, get_ai_config

__all__ = [
    "AIConfig",
    "AIRegistry",
    "CapabilityRegistry",
    "ExecutionPolicy",
    "PromptVersionService",
    "ProviderFactory",
    "ensure_bootstrapped",
    "get_ai_config",
    "get_ai_registry",
    "get_capability_registry",
    "get_provider_factory",
]


def __getattr__(name: str):
    if name == "get_ai_registry":
        from app.ai.providers.registry import get_ai_registry
        return get_ai_registry
    if name == "get_provider_factory":
        from app.ai.providers.factory import get_provider_factory
        return get_provider_factory
    if name == "ProviderFactory":
        from app.ai.providers.factory import ProviderFactory
        return ProviderFactory
    if name == "AIRegistry":
        from app.ai.providers.registry import AIRegistry
        return AIRegistry
    if name == "get_capability_registry":
        from app.ai.capability_registry import get_capability_registry
        return get_capability_registry
    if name == "CapabilityRegistry":
        from app.ai.capability_registry import CapabilityRegistry
        return CapabilityRegistry
    if name == "ensure_bootstrapped":
        from app.ai.bootstrap import ensure_bootstrapped
        return ensure_bootstrapped
    if name == "ExecutionPolicy":
        from app.ai.runtime.execution import ExecutionPolicy
        return ExecutionPolicy
    if name == "PromptVersionService":
        from app.ai.prompts.versioning import PromptVersionService
        return PromptVersionService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
