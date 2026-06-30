"""Bridges storyboard generator to shared AI registry."""

import json
import re

from app.domain.ai.providers.registry import get_provider_registry
from app.domain.ai.types import AIJobRequest
from app.domain.storyboard.providers.base import StoryboardProvider
from app.domain.storyboard.providers.demo import DemoStoryboardProvider, _parse_script_to_scenes
from app.domain.storyboard.types import StoryboardAgentRequest, StoryboardAgentResult


class LLMStoryboardProvider(StoryboardProvider):
    id = "llm"
    label = "LLM Storyboard Generator"

    def is_available(self) -> bool:
        registry = get_provider_registry()
        try:
            return registry.resolve("storyboard").is_available()
        except RuntimeError:
            return False

    def generate(self, request: StoryboardAgentRequest) -> StoryboardAgentResult:
        registry = get_provider_registry()
        ai_result = registry.generate(
            AIJobRequest(
                module="storyboard",
                prompt=request.prompt or "Convert script to storyboard scenes",
                parameters={
                    "action": request.action,
                    "title": request.project_title,
                    "script_excerpt": (request.script_content or "")[:12000],
                    "default_duration": request.default_duration_seconds,
                },
                project_id=request.project_id,
            )
        )
        scenes = _try_parse_scenes_json(ai_result.output_text)
        if not scenes:
            fallback = DemoStoryboardProvider()
            return fallback.generate(request)
        return StoryboardAgentResult(
            scenes=scenes,
            summary=ai_result.output_text[:500] if ai_result.output_text else "",
            provider=ai_result.provider,
            meta=ai_result.meta,
        )


def _try_parse_scenes_json(text: str | None) -> list[dict]:
    if not text:
        return []
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return []
    try:
        data = json.loads(match.group(0))
        if isinstance(data, list):
            return [s for s in data if isinstance(s, dict)]
    except json.JSONDecodeError:
        pass
    return []
