"""Unified AI providers package."""

from app.ai.providers.base import (
    CAPABILITIES,
    BaseProvider,
    EmbeddingsProvider,
    ImageProvider,
    LLMProvider,
    MusicProvider,
    TranslationProvider,
    VideoProvider,
    VoiceProvider,
)

__all__ = [
    "CAPABILITIES",
    "BaseProvider",
    "LLMProvider",
    "ImageProvider",
    "VideoProvider",
    "VoiceProvider",
    "MusicProvider",
    "TranslationProvider",
    "EmbeddingsProvider",
    "ProviderFactory",
    "get_provider_factory",
    "AIRegistry",
    "get_ai_registry",
]


def __getattr__(name: str):
    if name == "get_provider_factory":
        from app.ai.providers.factory import get_provider_factory
        return get_provider_factory
    if name == "ProviderFactory":
        from app.ai.providers.factory import ProviderFactory
        return ProviderFactory
    if name == "get_ai_registry":
        from app.ai.providers.registry import get_ai_registry
        return get_ai_registry
    if name == "AIRegistry":
        from app.ai.providers.registry import AIRegistry
        return AIRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
