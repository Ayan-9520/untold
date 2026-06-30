"""Bridges script writer to the shared AI provider registry."""

from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest
from app.domain.script.providers.base import ScriptProvider
from app.domain.script.types import ScriptAgentRequest, ScriptAgentResult


class LLMScriptProvider(ScriptProvider):
    id = "llm"
    label = "LLM Script Writer (via AI registry)"

    def is_available(self) -> bool:
        registry = get_provider_registry()
        try:
            p = registry.resolve("script")
            return p.is_available()
        except RuntimeError:
            return False

    def write(self, request: ScriptAgentRequest) -> ScriptAgentResult:
        registry = get_provider_registry()
        source = request.selection or request.content
        ai_result = registry.generate(
            AIJobRequest(
                module="script",
                prompt=request.prompt or request.action,
                parameters={
                    "action": request.action,
                    "title": request.title,
                    "style": request.style,
                    "selection": source[:8000] if source else "",
                    "target_language": request.target_language,
                    "tone": request.tone,
                },
                project_id=request.project_id,
            )
        )
        text = ai_result.output_text or ""
        if text and not text.strip().startswith("<"):
            text = f"<p>{text}</p>"
        return ScriptAgentResult(
            result=text,
            provider=ai_result.provider,
            meta=ai_result.meta,
        )
