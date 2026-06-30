"""High-level AI invocation with resilience and cost metadata."""

from __future__ import annotations

from typing import Any, Callable

from app.ai.bootstrap import ensure_bootstrapped
from app.ai.capability_registry import get_capability_registry
from app.ai.runtime.cost_tracking import attach_cost_metadata
from app.ai.runtime.execution import ExecutionPolicy, execute_with_resilience
from app.domain.ai.types import AIJobRequest, AIJobResult


def invoke_llm(request: AIJobRequest, provider_id: str | None = None) -> AIJobResult:
    ensure_bootstrapped()
    reg = get_capability_registry()
    provider = reg.resolve("llm", provider_id, module=request.module)

    def _op() -> AIJobResult:
        result = provider.generate(request)
        result.provider = getattr(provider, "id", provider_id or "demo")
        result.meta = attach_cost_metadata(
            result,
            capability="llm",
            provider_id=result.provider,
            prompt=request.prompt,
            output_text=result.output_text,
            meta=result.meta,
        )
        return result

    return execute_with_resilience(_op, policy=ExecutionPolicy())


def invoke_provider_method(
    capability: str,
    method: str,
    request: Any,
    provider_id: str | None = None,
    *,
    prompt_for_cost: str | None = None,
) -> Any:
    """Call provider.generate/translate/embed/etc. with resilience."""
    ensure_bootstrapped()
    provider = get_capability_registry().resolve(capability, provider_id)

    def _op():
        fn = getattr(provider, method)
        result = fn(request)
        if hasattr(result, "provider"):
            result.provider = provider.id
        if hasattr(result, "meta"):
            text = getattr(result, "output_text", None) or getattr(result, "translated_text", None)
            result.meta = attach_cost_metadata(
                result,
                capability=capability,
                provider_id=provider.id,
                prompt=prompt_for_cost or getattr(request, "text", None) or getattr(request, "prompt", None),
                output_text=text,
                meta=getattr(result, "meta", None),
            )
        return result

    return execute_with_resilience(_op, policy=ExecutionPolicy())


def embed_texts(texts: list[str], provider_id: str | None = None) -> list[list[float]]:
    ensure_bootstrapped()
    provider = get_capability_registry().resolve("embeddings", provider_id)

    def _op():
        return provider.embed(texts)

    return execute_with_resilience(_op, policy=ExecutionPolicy(timeout_seconds=60.0))
