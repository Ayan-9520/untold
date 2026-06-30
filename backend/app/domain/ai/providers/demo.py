"""Demo AI provider — works offline, no vendor credentials required."""

from app.domain.ai.providers.base import AIProvider
from app.domain.ai.types import AIJobRequest, AIJobResult
from app.domain.ai.telemetry import estimate_cost_usd, estimate_tokens, resolve_model

_MODULE_TEMPLATES: dict[str, str] = {
    "research": "Research brief:\n\n{prompt}\n\nSuggested angles: primary sources, timeline milestones, expert interviews.",
    "script": "SCRIPT — Scene draft\n\nNARRATOR: {prompt}\n\n[Cut to B-roll. Lower third with context.]",
    "image": "Image concept: {prompt}\n\nStyle: cinematic documentary, 16:9, high contrast, editorial lighting.",
    "video": "Video storyboard beat:\n\n{prompt}\n\nDuration: 8–12s · Camera: slow dolly · Mood: tense anticipation.",
    "voice": "Voice-over script (neutral documentary tone):\n\n\"{prompt}\"",
    "music": "Music brief: {prompt}\n\nTempo: 72 BPM · Key: D minor · Instruments: strings, subtle percussion.",
    "thumbnail": "Thumbnail concepts for: {prompt}\n\n1. Close-up face + bold title\n2. Split before/after\n3. High-contrast action frame",
    "seo": "SEO package for: {prompt}\n\nTitle: The Untold Story of …\nMeta: 155-char description with primary keyword.\nTags: documentary, sports, biography",
    "translation": "Translation (target locale from parameters):\n\n{prompt}",
    "shorts": "Short-form clip hook:\n\n{prompt}\n\n0–3s hook · 15s payoff · CTA overlay.",
}


class DemoProvider(AIProvider):
    id = "demo"
    label = "Demo Provider"
    supports_modules = frozenset(_MODULE_TEMPLATES.keys())

    def is_available(self) -> bool:
        return True

    def generate(self, request: AIJobRequest) -> AIJobResult:
        template = _MODULE_TEMPLATES.get(request.module, "AI output for {module}:\n\n{prompt}")
        text = template.format(module=request.module, prompt=request.prompt.strip())
        if request.parameters.get("target_language"):
            text = f"[{request.parameters['target_language'].upper()}]\n{text}"
        model = resolve_model(self.id, {"model": request.parameters.get("model")})
        input_tokens = estimate_tokens(request.prompt)
        output_tokens = estimate_tokens(text)
        return AIJobResult(
            output_text=text,
            meta={
                "provider": self.id,
                "simulated": True,
                "module": request.module,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": 420,
                "cost_usd": estimate_cost_usd(input_tokens, output_tokens, model),
            },
            provider=self.id,
        )
