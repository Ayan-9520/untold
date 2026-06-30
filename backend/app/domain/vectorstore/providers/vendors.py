"""Cloud vector database providers."""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.domain.vectorstore.providers.base import VectorStoreProvider
from app.domain.vectorstore.providers.demo import DemoVectorStoreProvider
from app.domain.vectorstore.providers.vectorstore_client import (
    chroma_search,
    chroma_upsert,
    milvus_search,
    milvus_upsert,
    pgvector_available,
    pgvector_ensure_collection,
    pgvector_search,
    pgvector_upsert,
    pinecone_search,
    pinecone_upsert,
    qdrant_ensure_collection,
    qdrant_search,
    qdrant_upsert,
    weaviate_search,
    weaviate_upsert,
)
from app.domain.vectorstore.types import (
    VectorSearchRequest,
    VectorSearchResult,
    VectorUpsertRequest,
    VectorUpsertResult,
)

logger = logging.getLogger("untold.vectorstore")


class _BaseCloudVectorStoreProvider(VectorStoreProvider):
    def _dimension(self, request: VectorUpsertRequest | VectorSearchRequest) -> int:
        if isinstance(request, VectorUpsertRequest) and request.dimension:
            return request.dimension
        if isinstance(request, VectorUpsertRequest) and request.records:
            return len(request.records[0].vector)
        return get_settings().vectorstore_dimension

    def _collection_name(self, collection: str) -> str:
        prefix = get_settings().vectorstore_collection_prefix.strip()
        return f"{prefix}_{collection}" if prefix else collection

    def _finish_upsert(self, request: VectorUpsertRequest, count: int, **meta) -> VectorUpsertResult:
        return VectorUpsertResult(
            upserted=count,
            collection=request.collection,
            provider=self.id,
            meta=meta,
        )

    def _finish_search(self, request: VectorSearchRequest, hits, **meta) -> VectorSearchResult:
        return VectorSearchResult(
            hits=hits,
            collection=request.collection,
            provider=self.id,
            meta=meta,
        )

    def _fallback_upsert(self, request: VectorUpsertRequest, error: str) -> VectorUpsertResult:
        logger.warning("%s upsert failed (%s), using demo fallback", self.id, error)
        result = DemoVectorStoreProvider().upsert(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result

    def _fallback_search(self, request: VectorSearchRequest, error: str) -> VectorSearchResult:
        logger.warning("%s search failed (%s), using demo fallback", self.id, error)
        result = DemoVectorStoreProvider().search(request)
        result.meta = dict(result.meta or {})
        result.meta["fallback"] = True
        result.meta["error"] = error
        result.meta["requested_provider"] = self.id
        return result


class PgVectorProvider(_BaseCloudVectorStoreProvider):
    id = "pgvector"
    label = "pgvector (PostgreSQL)"

    def is_available(self) -> bool:
        db = SessionLocal()
        try:
            return pgvector_available(db)
        except Exception:
            return False
        finally:
            db.close()

    def ensure_collection(self, collection: str, dimension: int) -> None:
        db = SessionLocal()
        try:
            pgvector_ensure_collection(db, self._collection_name(collection), dimension)
        finally:
            db.close()

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        db = SessionLocal()
        try:
            name = self._collection_name(request.collection)
            dim = self._dimension(request)
            self.ensure_collection(request.collection, dim)
            count = pgvector_upsert(db, name, request.records)
            return self._finish_upsert(request, count, engine="pgvector")
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))
        finally:
            db.close()

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        db = SessionLocal()
        try:
            name = self._collection_name(request.collection)
            hits = pgvector_search(db, name, request.vector, request.top_k)
            return self._finish_search(request, hits, engine="pgvector")
        except Exception as exc:
            return self._fallback_search(request, str(exc))
        finally:
            db.close()


class PineconeProvider(_BaseCloudVectorStoreProvider):
    id = "pinecone"
    label = "Pinecone"

    def is_available(self) -> bool:
        s = get_settings()
        return bool(s.pinecone_api_key and s.pinecone_index_host)

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        s = get_settings()
        try:
            count = pinecone_upsert(
                host=s.pinecone_index_host or "",
                api_key=s.pinecone_api_key or "",
                records=request.records,
                namespace=self._collection_name(request.collection),
            )
            return self._finish_upsert(request, count, namespace=self._collection_name(request.collection))
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        s = get_settings()
        try:
            hits = pinecone_search(
                host=s.pinecone_index_host or "",
                api_key=s.pinecone_api_key or "",
                vector=request.vector,
                top_k=request.top_k,
                namespace=self._collection_name(request.collection),
            )
            return self._finish_search(request, hits, namespace=self._collection_name(request.collection))
        except Exception as exc:
            return self._fallback_search(request, str(exc))


class WeaviateProvider(_BaseCloudVectorStoreProvider):
    id = "weaviate"
    label = "Weaviate"

    def is_available(self) -> bool:
        return bool(get_settings().weaviate_url)

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        s = get_settings()
        try:
            count = weaviate_upsert(
                url=s.weaviate_url,
                api_key=s.weaviate_api_key,
                collection=self._collection_name(request.collection),
                records=request.records,
            )
            return self._finish_upsert(request, count)
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        s = get_settings()
        try:
            hits = weaviate_search(
                url=s.weaviate_url,
                api_key=s.weaviate_api_key,
                collection=self._collection_name(request.collection),
                vector=request.vector,
                top_k=request.top_k,
            )
            return self._finish_search(request, hits)
        except Exception as exc:
            return self._fallback_search(request, str(exc))


class QdrantProvider(_BaseCloudVectorStoreProvider):
    id = "qdrant"
    label = "Qdrant"

    def is_available(self) -> bool:
        return bool(get_settings().qdrant_url)

    def ensure_collection(self, collection: str, dimension: int) -> None:
        s = get_settings()
        qdrant_ensure_collection(
            url=s.qdrant_url,
            api_key=s.qdrant_api_key,
            collection=self._collection_name(collection),
            dimension=dimension,
        )

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        s = get_settings()
        try:
            name = self._collection_name(request.collection)
            self.ensure_collection(request.collection, self._dimension(request))
            count = qdrant_upsert(
                url=s.qdrant_url,
                api_key=s.qdrant_api_key,
                collection=name,
                records=request.records,
            )
            return self._finish_upsert(request, count)
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        s = get_settings()
        try:
            hits = qdrant_search(
                url=s.qdrant_url,
                api_key=s.qdrant_api_key,
                collection=self._collection_name(request.collection),
                vector=request.vector,
                top_k=request.top_k,
            )
            return self._finish_search(request, hits)
        except Exception as exc:
            return self._fallback_search(request, str(exc))


class MilvusProvider(_BaseCloudVectorStoreProvider):
    id = "milvus"
    label = "Milvus"

    def is_available(self) -> bool:
        return bool(get_settings().milvus_uri)

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        s = get_settings()
        try:
            count = milvus_upsert(
                uri=s.milvus_uri,
                token=s.milvus_token,
                collection=self._collection_name(request.collection),
                records=request.records,
            )
            return self._finish_upsert(request, count)
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        s = get_settings()
        try:
            hits = milvus_search(
                uri=s.milvus_uri,
                token=s.milvus_token,
                collection=self._collection_name(request.collection),
                vector=request.vector,
                top_k=request.top_k,
            )
            return self._finish_search(request, hits)
        except Exception as exc:
            return self._fallback_search(request, str(exc))


class ChromaProvider(_BaseCloudVectorStoreProvider):
    id = "chroma"
    label = "Chroma"

    def is_available(self) -> bool:
        return bool(get_settings().chroma_url)

    def upsert(self, request: VectorUpsertRequest) -> VectorUpsertResult:
        s = get_settings()
        try:
            count = chroma_upsert(
                url=s.chroma_url,
                api_key=s.chroma_api_key,
                collection=self._collection_name(request.collection),
                records=request.records,
            )
            return self._finish_upsert(request, count)
        except Exception as exc:
            return self._fallback_upsert(request, str(exc))

    def search(self, request: VectorSearchRequest) -> VectorSearchResult:
        s = get_settings()
        try:
            hits = chroma_search(
                url=s.chroma_url,
                api_key=s.chroma_api_key,
                collection=self._collection_name(request.collection),
                vector=request.vector,
                top_k=request.top_k,
            )
            return self._finish_search(request, hits)
        except Exception as exc:
            return self._fallback_search(request, str(exc))


CLOUD_VECTORSTORE_PROVIDER_CLASSES: list[type[_BaseCloudVectorStoreProvider]] = [
    PgVectorProvider,
    PineconeProvider,
    WeaviateProvider,
    QdrantProvider,
    MilvusProvider,
    ChromaProvider,
]


def get_cloud_vectorstore_providers() -> list[VectorStoreProvider]:
    return [cls() for cls in CLOUD_VECTORSTORE_PROVIDER_CLASSES]
