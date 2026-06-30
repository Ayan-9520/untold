"""SEO API stub."""

from app.domain.seo.providers.base import SEOProvider
from app.domain.seo.providers.demo import DemoSEOProvider
from app.domain.seo.types import SEOGenerateRequest, SEOGenerateResult


class StubSEOProvider(SEOProvider):
    id = "seo_stub"
    label = "Cloud SEO API (configure keys)"

    def is_available(self) -> bool:
        return False

    def generate(self, request: SEOGenerateRequest) -> SEOGenerateResult:
        return DemoSEOProvider().generate(request)
