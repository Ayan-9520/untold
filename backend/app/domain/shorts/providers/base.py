"""Abstract shorts provider."""

from abc import ABC, abstractmethod

from app.domain.shorts.types import ShortsGenerateRequest, ShortsGenerateResult


class ShortsProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: ShortsGenerateRequest) -> ShortsGenerateResult:
        ...
