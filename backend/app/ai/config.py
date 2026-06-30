"""AI provider configuration — single source for keys, defaults, and enabled backends."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class AIConfig:
    default_provider: str
    enabled_providers: tuple[str, ...]
    openai_api_key: str | None
    openai_model: str
    embeddings_model: str
    anthropic_api_key: str | None
    anthropic_model: str
    gemini_api_key: str | None
    gemini_model: str
    openrouter_api_key: str | None
    openrouter_model: str
    groq_api_key: str | None
    groq_model: str
    ollama_base_url: str
    ollama_model: str
    azure_openai_api_key: str | None
    azure_openai_endpoint: str | None
    azure_openai_deployment: str | None
    azure_openai_api_version: str
    aws_bedrock_region: str
    aws_bedrock_model_id: str
    llm_default: str
    image_default: str
    image_enabled_providers: tuple[str, ...]
    openai_image_model: str
    google_imagen_api_key: str | None
    google_imagen_model: str
    stability_api_key: str | None
    flux_api_key: str | None
    ideogram_api_key: str | None
    replicate_api_token: str | None
    fal_api_key: str | None
    video_default: str
    video_enabled_providers: tuple[str, ...]
    runway_api_key: str | None
    luma_api_key: str | None
    pika_api_key: str | None
    kling_api_key: str | None
    hailuo_api_key: str | None
    voice_default: str
    voice_enabled_providers: tuple[str, ...]
    elevenlabs_api_key: str | None
    cartesia_api_key: str | None
    playht_api_key: str | None
    music_default: str
    music_enabled_providers: tuple[str, ...]
    suno_api_key: str | None
    udio_api_key: str | None
    stable_audio_api_key: str | None
    translation_default: str
    translation_enabled_providers: tuple[str, ...]
    google_translate_api_key: str | None
    deepl_api_key: str | None
    azure_translator_api_key: str | None
    embeddings_default: str
    embeddings_enabled_providers: tuple[str, ...]
    voyage_api_key: str | None
    cohere_api_key: str | None
    jina_api_key: str | None
    vectorstore_default: str
    vectorstore_enabled_providers: tuple[str, ...]
    pinecone_api_key: str | None
    qdrant_api_key: str | None
    research_default: str
    script_default: str
    seo_default: str
    shorts_default: str
    storyboard_default: str

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> AIConfig:
        s = settings or get_settings()
        enabled = tuple(x.strip() for x in s.ai_enabled_providers.split(",") if x.strip())
        return cls(
            default_provider=s.ai_default_provider,
            enabled_providers=enabled,
            openai_api_key=s.openai_api_key,
            openai_model=s.openai_model,
            embeddings_model=s.openai_embeddings_model,
            anthropic_api_key=s.anthropic_api_key,
            anthropic_model=s.anthropic_model,
            gemini_api_key=s.gemini_api_key,
            gemini_model=s.gemini_model,
            openrouter_api_key=s.openrouter_api_key,
            openrouter_model=s.openrouter_model,
            groq_api_key=s.groq_api_key,
            groq_model=s.groq_model,
            ollama_base_url=s.ollama_base_url,
            ollama_model=s.ollama_model,
            azure_openai_api_key=s.azure_openai_api_key,
            azure_openai_endpoint=s.azure_openai_endpoint,
            azure_openai_deployment=s.azure_openai_deployment,
            azure_openai_api_version=s.azure_openai_api_version,
            aws_bedrock_region=s.aws_bedrock_region,
            aws_bedrock_model_id=s.aws_bedrock_model_id,
            llm_default=s.ai_default_provider,
            image_default=s.image_default_provider,
            image_enabled_providers=tuple(
                x.strip() for x in s.image_enabled_providers.split(",") if x.strip()
            ),
            openai_image_model=s.openai_image_model,
            google_imagen_api_key=s.google_imagen_api_key,
            google_imagen_model=s.google_imagen_model,
            stability_api_key=s.stability_api_key,
            flux_api_key=s.flux_api_key,
            ideogram_api_key=s.ideogram_api_key,
            replicate_api_token=s.replicate_api_token,
            fal_api_key=s.fal_api_key,
            video_default=s.video_default_provider,
            video_enabled_providers=tuple(
                x.strip() for x in s.video_enabled_providers.split(",") if x.strip()
            ),
            runway_api_key=s.runway_api_key,
            luma_api_key=s.luma_api_key,
            pika_api_key=s.pika_api_key,
            kling_api_key=s.kling_api_key,
            hailuo_api_key=s.hailuo_api_key,
            voice_default=s.voice_default_provider,
            voice_enabled_providers=tuple(
                x.strip() for x in s.voice_enabled_providers.split(",") if x.strip()
            ),
            elevenlabs_api_key=s.elevenlabs_api_key,
            cartesia_api_key=s.cartesia_api_key,
            playht_api_key=s.playht_api_key,
            music_default=s.music_default_provider,
            music_enabled_providers=tuple(
                x.strip() for x in s.music_enabled_providers.split(",") if x.strip()
            ),
            suno_api_key=s.suno_api_key,
            udio_api_key=s.udio_api_key,
            stable_audio_api_key=s.stable_audio_api_key,
            translation_default=s.translation_default_provider,
            translation_enabled_providers=tuple(
                x.strip() for x in s.translation_enabled_providers.split(",") if x.strip()
            ),
            google_translate_api_key=s.google_translate_api_key,
            deepl_api_key=s.deepl_api_key,
            azure_translator_api_key=s.azure_translator_api_key,
            embeddings_default=s.embeddings_default_provider,
            embeddings_enabled_providers=tuple(
                x.strip() for x in s.embeddings_enabled_providers.split(",") if x.strip()
            ),
            voyage_api_key=s.voyage_api_key,
            cohere_api_key=s.cohere_api_key,
            jina_api_key=s.jina_api_key,
            vectorstore_default=s.vectorstore_default_provider,
            vectorstore_enabled_providers=tuple(
                x.strip() for x in s.vectorstore_enabled_providers.split(",") if x.strip()
            ),
            pinecone_api_key=s.pinecone_api_key,
            qdrant_api_key=s.qdrant_api_key,
            research_default=s.research_default_provider,
            script_default=s.script_default_provider,
            seo_default=s.seo_default_provider,
            shorts_default=s.shorts_default_provider,
            storyboard_default=s.storyboard_default_provider,
        )

    def default_for(self, capability: str) -> str:
        return {
            "llm": self.llm_default,
            "image": self.image_default,
            "video": self.video_default,
            "voice": self.voice_default,
            "music": self.music_default,
            "translation": self.translation_default,
            "embeddings": self.embeddings_default,
            "vectorstore": self.vectorstore_default,
        }.get(capability, self.default_provider)

    def is_provider_enabled(self, provider_id: str) -> bool:
        return not self.enabled_providers or provider_id in self.enabled_providers


@lru_cache
def get_ai_config() -> AIConfig:
    return AIConfig.from_settings()
