"""In-memory vector store for local development."""

from __future__ import annotations

import math
from typing import Any

from app.domain.vectorstore.providers.base import VectorStoreProvider
from app.domain.vectorstore.types import (
    VectorRecord,
    VectorSearchHit,
    VectorSearchRequest,
    VectorSearchResult,
    VectorUpsertRequest,
    VectorUpsertResult,
)

_store: dict[str, list[VectorRecord]] = {}


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


def _match_filter(metadata: dict[str, Any], flt: dict[str, Any] | None) -> bool:
    if not flt:
        return True
    for key, value in flt.items():
        if metadata.get(key) != value:
            return False
    return True


class DemoVectorStoreProvider(VectorStoreProvider):
    id = "demo"
    label = "Demo Vector Store (in-memory)"

    def is_available(self) -> bool:
        return True

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        bucket = _store.setdefault(request.collection, [])
        by_id = {r.id: r for r in bucket}
        for record in request.records:
            by_id[record.id] = record
        _store[request.collection] = list(by_id.values())
        return VectorUpsertResult(
            upserted=len(request.records),
            collection=request.collection,
            provider=self.id,
            meta={"simulated": True},
        )

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        records = _store.get(request.collection, [])
        scored: list[VectorSearchHit] = []
        for record in records:
            if not _match_filter(record.metadata, request.filter):
                continue
            scored.append(
                VectorSearchHit(
                    id=record.id,
                    text=record.text,
                    score=_cosine(request.vector, record.vector),
                    metadata=record.metadata,
                )
            )
        scored.sort(key=lambda h: h.score, reverse=True)
        return VectorSearchResult(
            hits=scored[: max(1, request.top_k)],
            collection=request.collection,
            provider=self.id,
            meta={"simulated": True},
        )

    def delete(self, collection: str, ids: list[str]) -> int:
        bucket = _store.get(collection, [])
        id_set = set(ids)
        kept = [r for r in bucket if r.id not in id_set]
        removed = len(bucket) - len(kept)
        _store[collection] = kept
        return removed
