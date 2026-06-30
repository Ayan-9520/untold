"""Bridge to external TTS APIs (ElevenLabs, Azure, Google) — stub until configured."""

from app.domain.voice.providers.base import VoiceProvider
from app.domain.voice.providers.demo import DemoVoiceProvider
from app.domain.voice.types import VoiceGenerateRequest, VoiceGenerateResult


class StubVoiceProvider(VoiceProvider):
    id = "voice_stub"
    label = "Cloud TTS API (configure keys)"

    def is_available(self) -> bool:
        return False

    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        return DemoVoiceProvider().generate(request)
