"""Demo embeddings — deterministic hash vectors for local dev."""

from __future__ import annotations

import hashlib
import math

from app.domain.embeddings.providers.base import EmbeddingsProvider

_DIM = 384


def demo_vector(text: str, dim: int = _DIM) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    for i in range(dim):
        byte = digest[i % len(digest)]
        values.append((byte / 127.5) - 1.0)
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


class DemoEmbeddingsProvider(EmbeddingsProvider):
    id = "demo"
    label = "Demo Embeddings"

    def is_available(self) -> bool:
        return True

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [demo_vector(t) for t in texts]
