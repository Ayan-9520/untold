"""Vector store — vendor-neutral types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VectorRecord:
    id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorUpsertRequest:
    collection: str
    records: list[VectorRecord]
    dimension: int | None = None


@dataclass
class VectorUpsertResult:
    upserted: int
    collection: str
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchRequest:
    collection: str
    vector: list[float]
    top_k: int = 10
    filter: dict[str, Any] | None = None


@dataclass
class VectorSearchHit:
    id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorSearchResult:
    hits: list[VectorSearchHit]
    collection: str
    provider: str = "demo"
    meta: dict[str, Any] = field(default_factory=dict)
