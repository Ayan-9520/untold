"""Demo video provider — original HTML motion clips + poster frame."""

from __future__ import annotations

import html
import uuid

from app.domain.storage.registry import upload_bytes
from app.domain.video.providers.base import VideoProvider
from app.domain.video.types import VIDEO_TYPES, VideoGenerateRequest, VideoGenerateResult

_TYPE_LABELS = {
    "b_roll": "B-roll",
    "drone": "Drone Style",
    "animation": "Animation",
    "sports_intro": "Sports Intro",
    "cinematic": "Cinematic Motion",
    "motion_graphics": "Motion Graphics",
    "slow_motion": "Slow Motion",
}

_ANIM = {
    "b_roll": "pan 8s linear infinite",
    "drone": "drift 10s ease-in-out infinite",
    "animation": "pulse 3s ease-in-out infinite",
    "sports_intro": "zoom 6s ease-in-out infinite",
    "cinematic": "fade 7s ease infinite",
    "motion_graphics": "slide 5s linear infinite",
    "slow_motion": "slow 12s linear infinite",
}


class DemoVideoProvider(VideoProvider):
    id = "demo"
    label = "Demo Video Generator (Motion HTML)"

    def is_available(self) -> bool:
        return True

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        video_type = request.video_type if request.video_type in VIDEO_TYPES else "b_roll"
        label = _TYPE_LABELS.get(video_type, "UNTOLD Motion")
        duration = max(4, min(request.duration_seconds, 30))
        anim = _ANIM.get(video_type, "pan 8s linear infinite")
        w, h = request.width, request.height
        if request.aspect_ratio == "9:16":
            w, h = 720, 1280
        elif request.aspect_ratio == "1:1":
            w, h = 720, 720

        safe_prompt = html.escape(request.prompt[:300])
        clip_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{html.escape(label)}</title>
<style>
*{{box-sizing:border-box;margin:0}} body{{background:#0a0a0f;color:#e5e7eb;font-family:system-ui,sans-serif;overflow:hidden;width:{w}px;height:{h}px}}
.bg{{position:absolute;inset:0;background:linear-gradient(135deg,#111827,#1e293b 50%,#0f172a)}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(201,162,39,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(201,162,39,.08) 1px,transparent 1px);background-size:40px 40px;animation:{anim}}}
.brand{{position:absolute;top:24px;left:24px;font-size:11px;letter-spacing:.2em;color:#c9a227}}
.title{{position:absolute;bottom:80px;left:32px;right:32px;font-size:22px;font-weight:700;line-height:1.3}}
.meta{{position:absolute;bottom:32px;left:32px;font-size:12px;color:#9ca3af}}
.bar{{position:absolute;bottom:0;left:0;height:4px;background:#c9a227;animation:grow {duration}s linear forwards}}
@keyframes grow{{from{{width:0}}to{{width:100%}}}}
@keyframes pan{{0%{{transform:translateX(0)}}100%{{transform:translateX(-40px)}}}}
@keyframes drift{{0%,100%{{transform:translateY(0) scale(1)}}50%{{transform:translateY(-12px) scale(1.02)}}}}
@keyframes pulse{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}
@keyframes zoom{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.05)}}}}
@keyframes fade{{0%,100%{{opacity:.85}}50%{{opacity:1}}}}
@keyframes slide{{0%{{transform:translateX(-20px)}}100%{{transform:translateX(20px)}}}}
@keyframes slow{{0%{{transform:translateX(0)}}100%{{transform:translateX(-10px)}}}}
</style></head><body>
<div class="bg"></div><div class="grid"></div>
<div class="brand">UNTOLD · ORIGINAL MOTION</div>
<div class="title">{safe_prompt}</div>
<div class="meta">{html.escape(label)} · {duration}s · demo clip</div>
<div class="bar"></div>
</body></html>"""

        folder = request.project_id or "studio"
        clip_key = f"ai-videos/{folder}/{uuid.uuid4().hex}.html"
        uploaded = upload_bytes(clip_key, clip_html.encode("utf-8"), "text/html")

        poster_svg = _poster_svg(label, request.prompt, w, h)
        poster_key = f"ai-videos/{folder}/{uuid.uuid4().hex}-poster.svg"
        poster_up = upload_bytes(poster_key, poster_svg.encode("utf-8"), "image/svg+xml")

        return VideoGenerateResult(
            output_text=f"Generated {label} clip ({duration}s): {request.prompt[:200]}",
            result_url=uploaded.url,
            preview_url=poster_up.url,
            r2_key=uploaded.key,
            mime_type="text/html",
            duration_seconds=duration,
            provider=self.id,
            meta={
                "video_type": video_type,
                "duration_seconds": duration,
                "fps": request.fps,
                "aspect_ratio": request.aspect_ratio,
                "width": w,
                "height": h,
                "format": "html_motion",
                "poster_url": poster_up.url,
                "simulated": True,
            },
        )


def _poster_svg(label: str, prompt: str, width: int, height: int) -> str:
    safe = html.escape(prompt[:120])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#111827"/><stop offset="100%" stop-color="#1e293b"/></linearGradient></defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <text x="50%" y="42%" text-anchor="middle" fill="#c9a227" font-family="system-ui" font-size="28" font-weight="bold">▶ UNTOLD</text>
  <text x="50%" y="52%" text-anchor="middle" fill="#e5e7eb" font-family="system-ui" font-size="18">{html.escape(label)}</text>
  <text x="50%" y="62%" text-anchor="middle" fill="#9ca3af" font-family="system-ui" font-size="13">{safe}</text>
</svg>"""
