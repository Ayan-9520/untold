"""Demo SEO provider — multi-variant metadata packs."""

from __future__ import annotations

from app.domain.seo.providers.base import SEOProvider
from app.domain.seo.scoring import score_variant
from app.domain.seo.types import CONTENT_TYPES, SEOGenerateRequest, SEOGenerateResult, SEOVariant

_STYLE_LABELS = ("Discovery", "Authority", "Engagement")


class DemoSEOProvider(SEOProvider):
    id = "demo"
    label = "Demo SEO Generator"

    def is_available(self) -> bool:
        return True

    def generate(self, request: SEOGenerateRequest) -> SEOGenerateResult:
        topic = request.topic.strip()
        ctype = request.content_type if request.content_type in CONTENT_TYPES else "video"
        kw = request.target_keyword or topic.split()[0] if topic.split() else "untold"
        count = max(1, min(request.variant_count, 5))
        variants: list[SEOVariant] = []

        for i in range(count):
            style = _STYLE_LABELS[i % len(_STYLE_LABELS)]
            yt_title = _youtube_title(topic, style, i)
            meta_title = yt_title[:58]
            desc = _description(topic, kw, ctype, style)
            keywords = _keywords(topic, kw)
            hashtags = _hashtags(kw, ctype)
            tags = keywords[:8]
            og = {
                "og:title": meta_title,
                "og:description": desc[:200],
                "og:type": "video.other" if ctype == "video" else "article",
                "og:site_name": "UNTOLD",
            }
            twitter = {
                "twitter:card": "summary_large_image",
                "twitter:title": meta_title,
                "twitter:description": desc[:200],
            }
            schema = {
                "@context": "https://schema.org",
                "@type": "VideoObject" if ctype in ("video", "shorts", "documentary") else "Article",
                "name": meta_title,
                "description": desc[:300],
                "keywords": ", ".join(keywords),
            }
            score, suggestions = score_variant(
                youtube_title=yt_title,
                meta_title=meta_title,
                description=desc,
                keywords=keywords,
                hashtags=hashtags,
            )
            variants.append(
                SEOVariant(
                    label=f"{style} variant",
                    youtube_title=yt_title,
                    meta_title=meta_title,
                    description=desc,
                    keywords=keywords,
                    hashtags=hashtags,
                    tags=tags,
                    open_graph=og,
                    twitter_cards=twitter,
                    schema_org=schema,
                    seo_score=score,
                    suggestions=suggestions,
                )
            )

        best = max(variants, key=lambda v: v.seo_score)
        return SEOGenerateResult(
            output_text=f"Generated {len(variants)} SEO variants. Best score: {best.seo_score}/100",
            variants=variants,
            provider=self.id,
            meta={"content_type": ctype, "target_keyword": kw, "variant_count": len(variants), "simulated": True},
        )


def _youtube_title(topic: str, style: str, idx: int) -> str:
    prefixes = {
        "Discovery": "The Untold Story of",
        "Authority": "Inside",
        "Engagement": "You Won't Believe",
    }
    prefix = prefixes.get(style, "UNTOLD:")
    base = f"{prefix} {topic}"[:65]
    return base if idx == 0 else f"{base} | Part {idx + 1}"[:70]


def _description(topic: str, kw: str, ctype: str, style: str) -> str:
    return (
        f"Explore {topic} in this original UNTOLD {ctype}. "
        f"Keyword focus: {kw}. {style} tone — crafted for search and social discovery. "
        f"Subscribe for documentaries, shorts, and stories the mainstream missed."
    )


def _keywords(topic: str, kw: str) -> list[str]:
    words = [w.lower() for w in topic.split() if len(w) > 3][:5]
    return list(dict.fromkeys([kw.lower(), "untold", "documentary", "sports", *words]))[:10]


def _hashtags(kw: str, ctype: str) -> list[str]:
    base = [f"#{kw.replace(' ', '')}", "#UNTOLD", "#SportsDoc"]
    if ctype == "shorts":
        base.append("#Shorts")
    return base[:8]
