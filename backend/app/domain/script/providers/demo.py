"""Demo script writer — broadcast-ready HTML without external APIs."""

import html

from app.domain.script.providers.base import ScriptProvider
from app.domain.script.types import STYLE_ACTIONS, ScriptAgentRequest, ScriptAgentResult


class DemoScriptProvider(ScriptProvider):
    id = "demo"
    label = "Demo Script Writer"

    def is_available(self) -> bool:
        return True

    def write(self, request: ScriptAgentRequest) -> ScriptAgentResult:
        action = request.action
        base = request.selection or request.content or request.title
        plain = _strip_html(base)[:400]
        prompt = (request.prompt or "").strip()
        title = request.title or "Untitled"
        lang = (request.target_language or "es").upper()
        tone = request.tone or "authoritative"

        result = ScriptAgentResult(provider=self.id, meta={"action": action, "simulated": True})
        esc = html.escape

        if action == "generate":
            result.result = (
                f"<h2>{esc(prompt or 'New section')}</h2>"
                f"<p><strong>Narrator:</strong> {esc(prompt or 'Open on a defining moment that frames the stakes.')}</p>"
                f"<p>Cut to archival footage. Lower third establishes context.</p>"
                f"<p><em>Interview subject:</em> Emotional beat tied to the central question about {esc(title)}.</p>"
            )
        elif action == "rewrite":
            result.result = f"<p>{esc(plain)} — revised for clarity, pacing, and broadcast-ready delivery.</p>"
        elif action == "expand":
            result.result = (
                f"<p>{esc(plain)}</p>"
                f"<p>Expanded with additional context, sensory detail, and narrative bridge to the next beat.</p>"
                f"<p><strong>Narrator:</strong> The wider story connects personal stakes to universal themes.</p>"
            )
        elif action == "shorten":
            short = plain[:120] + ("…" if len(plain) > 120 else "")
            result.result = f"<p><strong>Summary:</strong> {esc(short)}</p>"
        elif action == "grammar":
            result.result = f"<p>{esc(plain)}</p>"
        elif action == "tone":
            result.result = (
                f"<p><em>[{esc(tone)} tone]</em> {esc(plain)} — adjusted for voice, rhythm, and audience engagement.</p>"
            )
        elif action.startswith("style_"):
            style_name = STYLE_ACTIONS.get(action, action.replace("style_", ""))
            result.suggested_style = STYLE_ACTIONS.get(action)
            result.result = _style_block(style_name, plain, title)
        elif action == "translate":
            result.result = f"<p><em>[{lang}]</em> {esc(plain)}</p>"
        elif action == "chapter":
            result.result = (
                f"<h2>Chapter — {esc(prompt or 'Act II')}</h2>"
                f"<p><strong>Narrator:</strong> Chapter opening that reframes the documentary arc.</p>"
                f"<p>Scene transition. B-roll: {esc(title)} in context.</p>"
            )
        elif action == "scene":
            result.result = (
                f"<h3>Scene — {esc(prompt or 'Interview setup')}</h3>"
                f"<p><strong>INT. LOCATION — DAY</strong></p>"
                f"<p>Camera pushes in. Subject addresses the central tension.</p>"
                f"<p><em>Subject:</em> {esc(prompt or 'The moment everything changed was…')}</p>"
            )
        elif action == "hook":
            result.result = (
                f"<p><strong>HOOK:</strong> {esc(prompt or f'What if everything you knew about {title} was only half the story?')}</p>"
            )
        elif action == "cta":
            result.result = (
                f"<p><strong>CTA:</strong> {esc(prompt or 'Watch the full documentary on UNTOLD Originals — subscribe for untold stories.')}</p>"
            )
        else:
            result.result = f"<p>{esc(plain)}</p>"

        return result


def _strip_html(text: str) -> str:
    import re
    t = re.sub(r"<[^>]+>", " ", text or "")
    return " ".join(t.split())


def _style_block(style: str, plain: str, title: str) -> str:
    esc = html.escape
    templates = {
        "netflix": (
            f"<p><em>[Netflix documentary]</em> Cold open. Minimal score. "
            f"{esc(plain or f'This is the story of {title}.')}</p>"
            f"<p>Title card. Chapter break. Intimate vérité framing.</p>"
        ),
        "bbc": (
            f"<p><em>[BBC]</em> Measured, authoritative narration. "
            f"{esc(plain or f'For decades, {title} has shaped the record.')}</p>"
            f"<p>Archive stills. Expert testimony. Context before conclusion.</p>"
        ),
        "espn": (
            f"<p><em>[ESPN 30 for 30]</em> High energy. Personal stakes. "
            f"{esc(plain or f'{title} — legend, controversy, legacy.')}</p>"
            f"<p>Quick cuts. Stats on screen. Emotional payoff.</p>"
        ),
        "documentary": (
            f"<p><strong>Narrator:</strong> {esc(plain or f'In the world of {title}, truth is rarely simple.')}</p>"
            f"<p>B-roll. Natural sound. Journalistic pacing.</p>"
        ),
        "interview": (
            f"<p><strong>Interviewer:</strong> {esc(plain or 'Take us back to that moment.')}</p>"
            f"<p><em>Subject:</em> [Response — candid, first-person]</p>"
        ),
        "podcast": (
            f"<p><em>[Podcast]</em> Conversational hook. "
            f"{esc(plain or f'Today we unpack {title} — the story behind the headlines.')}</p>"
            f"<p>Ad break marker. Segment transition.</p>"
        ),
    }
    return templates.get(style, templates["documentary"])
