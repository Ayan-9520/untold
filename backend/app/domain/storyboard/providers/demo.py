"""Demo storyboard generator — structured scenes from script HTML."""

import html
import re

from app.domain.storyboard.providers.base import StoryboardProvider
from app.domain.storyboard.types import StoryboardAgentRequest, StoryboardAgentResult

MOODS = ["Tense", "Triumphant", "Reflective", "Intimate", "Epic", "Melancholic"]
TRANSITIONS = ["Cut", "Dissolve", "Fade to black", "Match cut", "Wipe", "Cross-dissolve"]
SHOT_TYPES = ["Establishing", "Wide", "Medium", "Close-up", "Extreme close-up", "OTS", "POV", "Aerial"]
CAMERA_ANGLES = ["Wide shot", "Medium shot", "Close-up", "Establishing", "Over-the-shoulder", "POV", "Aerial"]
CAMERA_MOVEMENTS = ["Static", "Pan left", "Pan right", "Slow pan", "Dolly in", "Dolly out", "Drone rise", "Handheld"]
LIGHTING = ["Natural", "Soft key", "Hard key", "Golden hour", "Low key", "High key", "Backlit"]
ENVIRONMENTS = ["Stadium", "Archive room", "Interview set", "Exterior location", "Studio", "Locker room"]


class DemoStoryboardProvider(StoryboardProvider):
    id = "demo"
    label = "Demo Storyboard Generator"

    def is_available(self) -> bool:
        return True

    def generate(self, request: StoryboardAgentRequest) -> StoryboardAgentResult:
        parsed = _parse_script_to_scenes(
            request.script_content,
            request.project_title,
            request.default_duration_seconds,
            request.prompt,
        )
        summary = (
            f"Generated {len(parsed)} scenes from script for **{request.project_title}**. "
            f"Each scene includes visual prompt, narration, dialogue cues, camera, lighting, mood, and transition."
        )
        if request.prompt:
            summary += f"\n\nFocus: {request.prompt}"
        return StoryboardAgentResult(
            scenes=parsed,
            summary=summary,
            provider=self.id,
            meta={"action": request.action, "scene_count": len(parsed), "simulated": True},
        )


def _strip_html(text: str) -> str:
    cleaned = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    return html.unescape(re.sub(r"\s+", " ", cleaned)).strip()


def _estimate_duration(text: str, default: int) -> int:
    words = len((text or "").split())
    if words == 0:
        return default
    return max(5, min(300, int(words / 2.5)))


def _extract_dialogue(text: str) -> str | None:
    for pattern in (
        r"(?:Subject|Interviewee|Guest|Athlete):\s*(.+?)(?:\.|$)",
        r"(?:Interviewer|Host):\s*(.+?)(?:\.|$)",
        r'"([^"]{8,})"',
    ):
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).strip()
    if "?" in text:
        return text.split("?")[0].strip() + "?"
    return None


def _scene_from_block(i: int, title: str, body: str, default_duration: int, project_title: str) -> dict:
    narration = body or title
    dialogue = _extract_dialogue(narration)
    idx = (i - 1) % len(MOODS)
    return {
        "scene_number": i,
        "sort_order": i,
        "duration_seconds": _estimate_duration(narration, default_duration),
        "visual_prompt": title or f"Scene {i} — {project_title}",
        "narration": narration,
        "dialogue": dialogue,
        "camera_angle": CAMERA_ANGLES[(i - 1) % len(CAMERA_ANGLES)],
        "camera_movement": CAMERA_MOVEMENTS[(i - 1) % len(CAMERA_MOVEMENTS)],
        "shot_type": SHOT_TYPES[(i - 1) % len(SHOT_TYPES)],
        "lighting": LIGHTING[(i - 1) % len(LIGHTING)],
        "environment": ENVIRONMENTS[(i - 1) % len(ENVIRONMENTS)],
        "mood": MOODS[idx],
        "transition": TRANSITIONS[(i - 1) % len(TRANSITIONS)],
        "reference_image_url": None,
        "status": "draft",
    }


def _parse_script_to_scenes(content: str, project_title: str, default_duration: int, focus: str | None) -> list[dict]:
    if not content or not content.strip():
        return [
            _scene_from_block(
                1,
                f"Opening — {project_title}",
                focus or "Cold open on defining moment. Establish stakes and central question.",
                default_duration,
                project_title,
            )
        ]

    scenes: list[dict] = []
    pattern = re.compile(r"<h([23])[^>]*>(.*?)</h\1>(.*?)(?=<h[23]|$)", re.I | re.S)
    matches = list(pattern.finditer(content))
    if matches:
        for i, match in enumerate(matches, start=1):
            title = _strip_html(match.group(2))
            body = _strip_html(match.group(3))
            scenes.append(_scene_from_block(i, title, body, default_duration, project_title))
        return scenes

    blocks = [b.strip() for b in re.split(r"</p>|</div>", content, flags=re.I) if b.strip()]
    paragraphs = []
    for block in blocks:
        text = _strip_html(block)
        if text and len(text) > 8:
            paragraphs.append(text)
    if not paragraphs:
        plain = _strip_html(content)
        if plain:
            paragraphs = [p.strip() for p in re.split(r"\n{2,}", plain) if p.strip()]

    for i, para in enumerate(paragraphs, start=1):
        title = para[:80] + ("…" if len(para) > 80 else "")
        scenes.append(_scene_from_block(i, title, para, default_duration, project_title))

    return scenes or [
        _scene_from_block(1, f"Opening — {project_title}", focus or "Documentary opening.", default_duration, project_title)
    ]
