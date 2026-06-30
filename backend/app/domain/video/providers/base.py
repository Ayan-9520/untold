"""Abstract video generation provider."""

from abc import ABC, abstractmethod

from app.domain.video.types import VideoGenerateRequest, VideoGenerateResult


class VideoProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: VideoGenerateRequest) -> VideoGenerateResult:
        ...
