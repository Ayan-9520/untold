"""SEO metadata generation types."""

from dataclasses import dataclass, field
from typing import Any


CONTENT_TYPES = ("video", "article", "documentary", "shorts", "podcast")


@dataclass
class SEOGenerateRequest:
    topic: str
    content_type: str = "video"
    target_keyword: str = ""
    variant_count: int = 3
    project_id: int | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class SEOVariant:
    label: str
    youtube_title: str
    meta_title: str
    description: str
    keywords: list[str]
    hashtags: list[str]
    tags: list[str]
    open_graph: dict[str, str]
    twitter_cards: dict[str, str]
    schema_org: dict[str, Any]
    seo_score: int
    suggestions: list[str]


@dataclass
class SEOGenerateResult:
    output_text: str = ""
    variants: list[SEOVariant] = field(default_factory=list)
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
