"""Bridges research agent to the shared AI provider registry (OpenAI, etc.)."""

from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest
from app.domain.research.providers.base import ResearchProvider
from app.domain.research.types import ResearchAgentRequest, ResearchAgentResult


class LLMResearchProvider(ResearchProvider):
    id = "llm"
    label = "LLM Research (via AI registry)"

    def is_available(self) -> bool:
        registry = get_provider_registry()
        try:
            p = registry.resolve("research")
            return p.id != "demo" or p.is_available()
        except RuntimeError:
            return False

    def research(self, request: ResearchAgentRequest) -> ResearchAgentResult:
        registry = get_provider_registry()
        ai_result = registry.generate(
            AIJobRequest(
                module="research",
                prompt=request.prompt,
                parameters={"action": request.action, "topic": request.topic, **request.context},
                project_id=request.project_id,
            )
        )
        text = ai_result.output_text
        return ResearchAgentResult(
            summary=text,
            suggestions=[
                "Verify all statistics against primary sources",
                "Document conflicting narratives",
                "Add interview targets",
            ],
            follow_up_questions=[
                f"What gaps remain in the research on {request.topic}?",
                "Which claims need independent fact-checking?",
            ],
            provider=ai_result.provider,
            meta=ai_result.meta,
        )
