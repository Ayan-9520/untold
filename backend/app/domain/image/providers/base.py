"""Abstract image generation provider."""

from abc import ABC, abstractmethod

from app.domain.image.types import ImageGenerateRequest, ImageGenerateResult


class ImageProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        ...
