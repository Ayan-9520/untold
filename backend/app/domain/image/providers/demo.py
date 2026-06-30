"""Demo image provider — original SVG artwork uploaded to cloud storage."""

from __future__ import annotations

import html
import textwrap
import uuid

from app.domain.image.providers.base import ImageProvider
from app.domain.image.types import IMAGE_TYPES, ImageGenerateRequest, ImageGenerateResult
from app.domain.storage.registry import upload_bytes

_TYPE_LABELS = {
    "poster": "Documentary Poster",
    "thumbnail": "Video Thumbnail",
    "concept_art": "Concept Art",
    "environment": "Environment Design",
    "illustration": "Illustration",
    "sports": "Sports Artwork",
    "background": "Background Image",
}

_TYPE_COLORS = {
    "poster": ("#1a1a2e", "#c9a227"),
    "thumbnail": ("#0f172a", "#f59e0b"),
    "concept_art": ("#1e293b", "#38bdf8"),
    "environment": ("#14532d", "#86efac"),
    "illustration": ("#312e81", "#a78bfa"),
    "sports": ("#7f1d1d", "#fca5a5"),
    "background": ("#0c4a6e", "#7dd3fc"),
}


class DemoImageProvider(ImageProvider):
    id = "demo"
    label = "Demo Image Generator (SVG)"

    def is_available(self) -> bool:
        return True

    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        image_type = request.image_type if request.image_type in IMAGE_TYPES else "illustration"
        label = _TYPE_LABELS.get(image_type, "UNTOLD Original")
        bg, accent = _TYPE_COLORS.get(image_type, ("#111827", "#c9a227"))

        action_label = ""
        if request.action == "upscale":
            action_label = " · 2× Upscaled"
            request.width = min(request.width * 2, 2048)
            request.height = min(request.height * 2, 2048)
        elif request.action == "variation":
            action_label = " · Variation"

        safe_prompt = html.escape(request.prompt[:280])
        wrapped = html.escape("\n".join(textwrap.wrap(request.prompt[:120], width=42)))

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{request.width}" height="{request.height}" viewBox="0 0 {request.width} {request.height}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg}"/>
      <stop offset="100%" style="stop-color:#000"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <rect x="40" y="40" width="{request.width - 80}" height="{request.height - 80}" fill="none" stroke="{accent}" stroke-width="3" opacity="0.6"/>
  <text x="50%" y="18%" text-anchor="middle" fill="{accent}" font-family="Georgia,serif" font-size="28" font-weight="bold">UNTOLD STUDIO</text>
  <text x="50%" y="26%" text-anchor="middle" fill="#e5e7eb" font-family="system-ui,sans-serif" font-size="20">{html.escape(label)}{html.escape(action_label)}</text>
  <text x="50%" y="38%" text-anchor="middle" fill="#9ca3af" font-family="system-ui,sans-serif" font-size="14">{request.aspect_ratio} · Original artwork only</text>
  <foreignObject x="8%" y="44%" width="84%" height="40%">
    <div xmlns="http://www.w3.org/1999/xhtml" style="color:#d1d5db;font-family:system-ui,sans-serif;font-size:15px;line-height:1.5;text-align:center;padding:12px;">
      {safe_prompt}
    </div>
  </foreignObject>
  <text x="50%" y="92%" text-anchor="middle" fill="#6b7280" font-family="monospace" font-size="11">demo · {wrapped[:60]}…</text>
</svg>"""

        data = svg.encode("utf-8")
        folder = request.project_id or "studio"
        key = f"ai-images/{folder}/{uuid.uuid4().hex}.svg"
        uploaded = upload_bytes(key, data, "image/svg+xml")

        return ImageGenerateResult(
            output_text=f"Generated {label}: {request.prompt[:200]}",
            result_url=uploaded.url,
            r2_key=uploaded.key,
            mime_type="image/svg+xml",
            size_bytes=uploaded.size_bytes,
            provider=self.id,
            meta={
                "image_type": image_type,
                "action": request.action,
                "aspect_ratio": request.aspect_ratio,
                "width": request.width,
                "height": request.height,
                "simulated": True,
            },
        )
