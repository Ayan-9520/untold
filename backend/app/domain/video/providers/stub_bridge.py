"""Bridge to external video APIs (Runway, Replicate, etc.) — stub until configured."""

from app.domain.video.providers.base import VideoProvider
from app.domain.video.providers.demo import DemoVideoProvider
from app.domain.video.types import VideoGenerateRequest, VideoGenerateResult


class StubVideoProvider(VideoProvider):
    id = "video_stub"
    label = "Cloud Video API (configure keys)"

    def is_available(self) -> bool:
        return False

    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        return DemoVideoProvider().generate(request)
