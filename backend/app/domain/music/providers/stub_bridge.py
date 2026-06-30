"""Bridge to external music APIs (Suno, Udio, etc.) — stub until configured."""

from app.domain.music.providers.base import MusicProvider
from app.domain.music.providers.demo import DemoMusicProvider
from app.domain.music.types import MusicGenerateRequest, MusicGenerateResult


class StubMusicProvider(MusicProvider):
    id = "music_stub"
    label = "Cloud Music API (configure keys)"

    def is_available(self) -> bool:
        return False

    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        return DemoMusicProvider().generate(request)
