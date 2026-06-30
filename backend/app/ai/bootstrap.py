"""Bootstrap all AI providers into the single capability registry."""

from __future__ import annotations

import logging

from app.ai.capability_registry import get_capability_registry
from app.domain.ai.providers.media_stub import MediaStubProvider

logger = logging.getLogger("untold.ai.bootstrap")

_bootstrapped = False


def ensure_bootstrapped() -> None:
    global _bootstrapped
    if _bootstrapped:
        return

    reg = get_capability_registry()

    # LLM
    from app.ai.providers.llm import get_llm_providers
    from app.domain.ai.providers.llm_bridge import LLMProviderBridge

    for llm in get_llm_providers():
        reg.register("llm", LLMProviderBridge(llm))
    reg.register("llm", MediaStubProvider())

    # Embeddings
    from app.domain.embeddings.providers.demo import DemoEmbeddingsProvider
    from app.domain.embeddings.providers.vendors import get_cloud_embeddings_providers

    reg.register("embeddings", DemoEmbeddingsProvider())
    for p in get_cloud_embeddings_providers():
        reg.register("embeddings", p)

    # Image
    from app.domain.image.providers.demo import DemoImageProvider
    from app.domain.image.providers.vendors import get_cloud_image_providers

    reg.register("image", DemoImageProvider())
    for p in get_cloud_image_providers():
        reg.register("image", p)

    # Video
    from app.domain.video.providers.demo import DemoVideoProvider
    from app.domain.video.providers.vendors import get_cloud_video_providers

    reg.register("video", DemoVideoProvider())
    for p in get_cloud_video_providers():
        reg.register("video", p)

    # Voice
    from app.domain.voice.providers.demo import DemoVoiceProvider
    from app.domain.voice.providers.vendors import get_cloud_voice_providers

    reg.register("voice", DemoVoiceProvider())
    for p in get_cloud_voice_providers():
        reg.register("voice", p)

    # Music
    from app.domain.music.providers.demo import DemoMusicProvider
    from app.domain.music.providers.vendors import get_cloud_music_providers

    reg.register("music", DemoMusicProvider())
    for p in get_cloud_music_providers():
        reg.register("music", p)

    # Translation
    from app.domain.translation.providers.demo import DemoTranslationProvider
    from app.domain.translation.providers.vendors import get_cloud_translation_providers

    reg.register("translation", DemoTranslationProvider())
    for p in get_cloud_translation_providers():
        reg.register("translation", p)

    # Vector store
    from app.domain.vectorstore.providers.demo import DemoVectorStoreProvider
    from app.domain.vectorstore.providers.vendors import get_cloud_vectorstore_providers

    reg.register("vectorstore", DemoVectorStoreProvider())
    for p in get_cloud_vectorstore_providers():
        reg.register("vectorstore", p)

    _bootstrapped = True
    caps = sum(len(reg.providers_for(c)) for c in ("llm", "image", "video", "voice", "music", "translation", "embeddings", "vectorstore"))
    logger.info("AI capability registry bootstrapped (%s providers)", caps)


def sync_domain_registry(domain_registry, capability: str) -> None:
    """Populate a legacy domain registry from the canonical capability registry."""
    ensure_bootstrapped()
    reg = get_capability_registry()
    for provider in reg.providers_for(capability).values():
        if hasattr(domain_registry, "register"):
            domain_registry.register(provider)
