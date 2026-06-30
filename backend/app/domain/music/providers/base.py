"""Abstract music generation provider."""

from abc import ABC, abstractmethod

from app.domain.music.types import MusicGenerateRequest, MusicGenerateResult


class MusicProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: MusicGenerateRequest) -> MusicGenerateResult:
        ...

    def preview(self, request: MusicGenerateRequest, max_seconds: int = 12) -> MusicGenerateResult:
        short = MusicGenerateRequest(
            prompt=request.prompt,
            category=request.category,
            duration_seconds=min(max_seconds, request.duration_seconds),
            loop=request.loop,
            fade_in_seconds=min(request.fade_in_seconds, 1.0),
            fade_out_seconds=min(request.fade_out_seconds, 1.5),
            project_id=request.project_id,
        )
        return self.generate(short)
