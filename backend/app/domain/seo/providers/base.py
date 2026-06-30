"""Abstract SEO provider."""

from abc import ABC, abstractmethod

from app.domain.seo.types import SEOGenerateRequest, SEOGenerateResult


class SEOProvider(ABC):
    id: str
    label: str

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def generate(self, request: SEOGenerateRequest) -> SEOGenerateResult:
        ...
