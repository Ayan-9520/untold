"""LLM providers — OpenAI, Claude, Gemini, OpenRouter, Groq, Ollama, Azure, Bedrock."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

from app.ai.config import get_ai_config
from app.ai.providers.base import LLMProvider
from app.ai.providers.llm_client import (
    bedrock_available,
    chat_anthropic,
    chat_azure_openai,
    chat_bedrock,
    chat_gemini,
    chat_ollama,
    chat_openai_compatible,
    ollama_reachable,
    system_prompt_for,
)
from app.core.config import get_settings
from app.domain.ai.providers.demo import DemoProvider
from app.domain.ai.types import AIJobRequest

logger = logging.getLogger("untold.ai.llm")

TEXT_MODULES: frozenset[str] = frozenset({
    "research",
    "script",
    "storyboard",
    "seo",
    "translation",
    "thumbnail",
    "shorts",
    "voice",
    "music",
})


class _BaseLLM(LLMProvider):
    supports_modules: ClassVar[frozenset[str]] = TEXT_MODULES

    def supports(self, module: str) -> bool:
        return module in self.supports_modules

    def _fallback(self, module: str, prompt: str, parameters: dict | None, error: str) -> dict[str, Any]:
        logger.warning("%s failed (%s), using demo fallback", self.id, error)
        result = DemoProvider().generate(
            AIJobRequest(module=module, prompt=prompt, parameters=parameters or {})
        )
        meta = dict(result.meta or {})
        meta["fallback"] = True
        meta["error"] = error
        return {
            "output_text": result.output_text,
            "result_url": result.result_url,
            "meta": meta,
            "provider": self.id,
        }

    def _ok(self, text: str, model: str, **extra_meta: Any) -> dict[str, Any]:
        return {
            "output_text": text,
            "result_url": None,
            "meta": {"provider": self.id, "model": model, **extra_meta},
            "provider": self.id,
        }


class DemoLLMProvider(_BaseLLM):
    id = "demo"
    label = "Demo"

    def is_available(self) -> bool:
        return True

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        result = DemoProvider().generate(
            AIJobRequest(module=module, prompt=prompt, parameters=parameters or {})
        )
        return {
            "output_text": result.output_text,
            "result_url": result.result_url,
            "meta": result.meta,
            "provider": self.id,
        }


class OpenAIProvider(_BaseLLM):
    id = "openai"
    label = "OpenAI"

    def is_available(self) -> bool:
        return bool(get_settings().openai_api_key)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_openai_compatible(
                url="https://api.openai.com/v1/chat/completions",
                api_key=s.openai_api_key or "",
                model=s.openai_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.openai_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class ClaudeProvider(_BaseLLM):
    id = "claude"
    label = "Claude"

    def is_available(self) -> bool:
        return bool(get_settings().anthropic_api_key)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_anthropic(
                api_key=s.anthropic_api_key or "",
                model=s.anthropic_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.anthropic_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class GeminiProvider(_BaseLLM):
    id = "gemini"
    label = "Gemini"

    def is_available(self) -> bool:
        return bool(get_settings().gemini_api_key)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_gemini(
                api_key=s.gemini_api_key or "",
                model=s.gemini_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.gemini_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class OpenRouterProvider(_BaseLLM):
    id = "openrouter"
    label = "OpenRouter"

    def is_available(self) -> bool:
        return bool(get_settings().openrouter_api_key)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_openai_compatible(
                url="https://openrouter.ai/api/v1/chat/completions",
                api_key=s.openrouter_api_key or "",
                model=s.openrouter_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
                extra_headers={
                    "HTTP-Referer": "https://untold.studio",
                    "X-Title": "UNTOLD Studio",
                },
            )
            return self._ok(text, s.openrouter_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class GroqProvider(_BaseLLM):
    id = "groq"
    label = "Groq"

    def is_available(self) -> bool:
        return bool(get_settings().groq_api_key)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_openai_compatible(
                url="https://api.groq.com/openai/v1/chat/completions",
                api_key=s.groq_api_key or "",
                model=s.groq_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.groq_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class OllamaProvider(_BaseLLM):
    id = "ollama"
    label = "Ollama"

    def is_available(self) -> bool:
        s = get_settings()
        return ollama_reachable(s.ollama_base_url)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_ollama(
                base_url=s.ollama_base_url,
                model=s.ollama_model,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.ollama_model)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class AzureOpenAIProvider(_BaseLLM):
    id = "azure_openai"
    label = "Azure OpenAI"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.azure_openai_api_key and s.azure_openai_endpoint and s.azure_openai_deployment)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_azure_openai(
                endpoint=s.azure_openai_endpoint or "",
                deployment=s.azure_openai_deployment or "",
                api_key=s.azure_openai_api_key or "",
                api_version=s.azure_openai_api_version,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.azure_openai_deployment or "")
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


class BedrockProvider(_BaseLLM):
    id = "bedrock"
    label = "AWS Bedrock"

    def is_available(self) -> bool:
        s = get_settings()
        return bedrock_available(s.aws_bedrock_region)

    def complete(self, *, module: str, prompt: str, parameters: dict | None = None) -> dict[str, Any]:
        s = get_settings()
        try:
            text = chat_bedrock(
                region=s.aws_bedrock_region,
                model_id=s.aws_bedrock_model_id,
                user_prompt=prompt,
                system=system_prompt_for(module),
            )
            return self._ok(text, s.aws_bedrock_model_id)
        except Exception as exc:
            return self._fallback(module, prompt, parameters, str(exc))


LLM_PROVIDER_CLASSES: list[type[_BaseLLM]] = [
    DemoLLMProvider,
    OpenAIProvider,
    ClaudeProvider,
    GeminiProvider,
    OpenRouterProvider,
    GroqProvider,
    OllamaProvider,
    AzureOpenAIProvider,
    BedrockProvider,
]


def get_llm_providers() -> list[LLMProvider]:
    return [cls() for cls in LLM_PROVIDER_CLASSES]


def get_llm_provider(provider_id: str) -> LLMProvider | None:
    for provider in get_llm_providers():
        if provider.id == provider_id:
            return provider
    return None
