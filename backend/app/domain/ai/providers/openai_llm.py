"""OpenAI-compatible LLM provider — optional, only active when API key is set."""

import logging

from app.domain.ai.providers.base import AIProvider
from app.domain.ai.types import AIJobRequest, AIJobResult

logger = logging.getLogger("untold.ai.openai")

_TEXT_MODULES = frozenset({
    "research", "script", "seo", "translation", "thumbnail", "shorts", "voice", "music",
})


class OpenAILLMProvider(AIProvider):
    id = "openai"
    label = "OpenAI LLM"
    supports_modules = _TEXT_MODULES

    def is_available(self) -> bool:
        from app.core.config import get_settings

        return bool(get_settings().openai_api_key)

    def generate(self, request: AIJobRequest) -> AIJobResult:
        from app.core.config import get_settings

        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OpenAI provider not configured")

        try:
            from app.services.news_ai_service import NewsAIService

            topic = request.parameters.get("topic") or request.prompt[:80]
            style = request.parameters.get("style", "documentary")
            result = NewsAIService._generate_all(request.prompt, topic, style, request.module)
            output = (
                result.get("rewritten_content")
                or result.get("summary")
                or result.get("title")
                or str(result)
            )
            return AIJobResult(
                output_text=output,
                meta={"provider": self.id, "model": settings.openai_model, "raw_keys": list(result.keys())},
                provider=self.id,
            )
        except Exception as exc:
            logger.warning("OpenAI generation failed, falling back to demo output: %s", exc)
            from app.domain.ai.providers.demo import DemoProvider

            fallback = DemoProvider().generate(request)
            fallback.meta["openai_error"] = str(exc)
            fallback.meta["fallback"] = True
            return fallback
