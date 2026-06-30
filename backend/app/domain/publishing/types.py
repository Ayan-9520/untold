"""Publishing agent — platform labels and request types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

PUBLISH_PLATFORMS = (
    ("originals", "UNTOLD Originals"),
    ("youtube", "YouTube"),
    ("instagram", "Instagram"),
    ("facebook", "Facebook"),
    ("x", "X"),
    ("threads", "Threads"),
)

WEBHOOK_EVENTS = (
    "publish.queued",
    "publish.scheduled",
    "publish.approved",
    "publish.rejected",
    "publish.success",
    "publish.failed",
    "publish.retry",
)

PLATFORM_LABELS = dict(PUBLISH_PLATFORMS)


@dataclass
class PublishRequest:
    project_id: int
    platforms: list[str]
    scheduled_at: datetime | None = None
    requires_approval: bool = True
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: list[str] = field(default_factory=list)
    thumbnail_url: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishResult:
    platform: str
    success: bool
    job_id: int | None = None
    external_id: str | None = None
    error: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
