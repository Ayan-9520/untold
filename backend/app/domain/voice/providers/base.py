"""Abstract voice generation provider."""

from abc import ABC, abstractmethod

from app.domain.voice.types import VoiceGenerateRequest, VoiceGenerateResult


class VoiceProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: VoiceGenerateRequest) -> VoiceGenerateResult:
        ...

    def preview(self, request: VoiceGenerateRequest, max_chars: int = 120) -> VoiceGenerateResult:
        short = VoiceGenerateRequest(
            text=request.text[:max_chars],
            language=request.language,
            emotion=request.emotion,
            pitch=request.pitch,
            speed=request.speed,
            voice_id=request.voice_id,
            translate_to=None,
            sync_subtitles=False,
            project_id=request.project_id,
        )
        return self.generate(short)
