"""Translation provider abstraction."""

from abc import ABC, abstractmethod

from app.domain.translation.types import TranslationRequest, TranslationResult


class TranslationProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def translate(self, request: TranslationRequest) -> TranslationResult:
        ...
