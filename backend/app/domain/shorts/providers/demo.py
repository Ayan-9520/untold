"""Demo shorts provider — highlight detection + vertical clips."""

from __future__ import annotations

import html
import uuid

from app.domain.shorts.highlights import detect_highlights
from app.domain.shorts.providers.base import ShortsProvider
from app.domain.shorts.types import PLATFORM_LABELS, SHORTS_PLATFORMS, ShortsGenerateRequest, ShortsGenerateResult
from app.domain.storage.registry import upload_bytes

_HASHTAGS = {
    "instagram_reels": ["#Reels", "#SportsDoc", "#UntoldStories", "#Vertical"],
    "youtube_shorts": ["#Shorts", "#Documentary", "#SportsHistory", "#YouTubeShorts"],
    "tiktok": ["#TikTokSports", "#StoryTime", "#FYP", "#DocuTok"],
    "facebook_reels": ["#FacebookReels", "#Sports", "#OriginalContent", "#WatchNow"],
}


class DemoShortsProvider(ShortsProvider):
    id = "demo"
    label = "Demo Shorts Generator"

    def is_available(self) -> bool:
        return True

    def generate(self, request: ShortsGenerateRequest) -> ShortsGenerateResult:
        topic = request.topic or "UNTOLD highlight reel"
        platforms = [p for p in request.platforms if p in SHORTS_PLATFORMS] or list(SHORTS_PLATFORMS)
        highlights = detect_highlights(topic, request.source_video_url) if request.auto_highlights else []
        hook = f"Wait for the moment nobody talks about in {topic[:80]}…" if request.hook_optimization else topic[:100]

        folder = request.project_id or "studio"
        clips: list[dict] = []
        for plat in platforms:
            label = PLATFORM_LABELS.get(plat, plat)
            hl = highlights[0] if highlights else {"start_seconds": 0, "end_seconds": request.clip_duration_seconds}
            zoom = "zoom 4s ease-in-out infinite" if request.auto_zoom else "none"
            cap = (
                f'<div class="cap">{html.escape(hook)}</div>'
                if request.captions
                else ""
            )
            clip_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{margin:0;width:720px;height:1280px;background:#0a0a0f;color:#fff;font-family:system-ui,sans-serif;overflow:hidden}}
.bg{{position:absolute;inset:0;background:linear-gradient(160deg,#111827,#1e1b4b)}}
.frame{{position:absolute;inset:0;animation:{zoom}}}
.brand{{position:absolute;top:32px;left:24px;font-size:11px;color:#c9a227;letter-spacing:.15em}}
.hook{{position:absolute;bottom:200px;left:24px;right:24px;font-size:26px;font-weight:700;line-height:1.2}}
.cap{{position:absolute;bottom:80px;left:24px;right:24px;font-size:14px;color:#e5e7eb;background:rgba(0,0,0,.5);padding:8px;border-radius:8px}}
.meta{{position:absolute;bottom:32px;left:24px;font-size:12px;color:#9ca3af}}
@keyframes zoom{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}}
</style></head><body>
<div class="bg"></div><div class="frame"><div class="bg"></div></div>
<div class="brand">UNTOLD · {html.escape(label)}</div>
<div class="hook">{html.escape(hook)}</div>
{cap}
<div class="meta">9:16 · {hl['start_seconds']}s–{hl['end_seconds']}s · demo clip</div>
</body></html>"""
            key = f"ai-shorts/{folder}/{uuid.uuid4().hex}-{plat}.html"
            up = upload_bytes(key, clip_html.encode("utf-8"), "text/html")
            clips.append({
                "platform": plat,
                "platform_label": label,
                "url": up.url,
                "r2_key": up.key,
                "highlight": hl,
                "duration_seconds": request.clip_duration_seconds,
                "aspect_ratio": request.aspect_ratio,
            })

        thumb_svg = _thumbnail_svg(topic, hook)
        thumb_key = f"ai-shorts/{folder}/{uuid.uuid4().hex}-thumb.svg"
        thumb_up = upload_bytes(thumb_key, thumb_svg.encode("utf-8"), "image/svg+xml")

        tags = []
        for plat in platforms:
            tags.extend(_HASHTAGS.get(plat, [])[:3])
        tags = list(dict.fromkeys(tags))[:12]

        vtt = None
        if request.captions:
            vtt = f"WEBVTT\n\n00:00:00.000 --> 00:00:{request.clip_duration_seconds:02d}.000\n{hook}\n"

        primary = clips[0]["url"] if clips else None
        primary_key = clips[0]["r2_key"] if clips else None

        return ShortsGenerateResult(
            output_text=f"Generated {len(clips)} vertical shorts from source video. Highlights: {len(highlights)}",
            result_url=primary,
            r2_key=primary_key,
            mime_type="text/html",
            provider=self.id,
            highlights=highlights,
            clips=clips,
            thumbnail_url=thumb_up.url,
            hashtags=tags,
            hook=hook,
            captions_vtt=vtt,
            meta={
                "source_video_url": request.source_video_url,
                "platforms": platforms,
                "auto_highlights": request.auto_highlights,
                "captions": request.captions,
                "auto_zoom": request.auto_zoom,
                "hook_optimization": request.hook_optimization,
                "aspect_ratio": request.aspect_ratio,
                "simulated": True,
            },
        )


def _thumbnail_svg(topic: str, hook: str) -> str:
    safe = html.escape(topic[:60])
    hook_safe = html.escape(hook[:80])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280">
  <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#312e81"/></linearGradient></defs>
  <rect width="720" height="1280" fill="url(#g)"/>
  <text x="360" y="520" text-anchor="middle" fill="#c9a227" font-family="system-ui" font-size="32" font-weight="bold">▶ SHORT</text>
  <text x="360" y="580" text-anchor="middle" fill="#fff" font-family="system-ui" font-size="22">{safe}</text>
  <text x="360" y="640" text-anchor="middle" fill="#9ca3af" font-family="system-ui" font-size="16">{hook_safe}</text>
</svg>"""
