"""Demo platform publisher."""

from __future__ import annotations

import random
import uuid

from app.domain.publishing.types import PublishResult


class DemoPlatformPublisher:
    """Simulates multi-platform publish with occasional failures."""

    def publish(
        self,
        platform: str,
        *,
        project_title: str,
        seo_title: str | None = None,
        retry_count: int = 0,
    ) -> PublishResult:
        label = seo_title or project_title
        fail_chance = 0.06 if retry_count == 0 else 0.02
        if platform != "originals" and random.random() < fail_chance:
            return PublishResult(
                platform=platform,
                success=False,
                error=f"{platform} API temporarily unavailable",
            )
        return PublishResult(
            platform=platform,
            success=True,
            external_id=f"{platform}-{uuid.uuid4().hex[:12]}",
            meta={"simulated": True, "title": label[:120]},
        )
