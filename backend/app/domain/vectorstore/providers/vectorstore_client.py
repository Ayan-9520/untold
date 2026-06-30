"""Shared vector database HTTP / SQL clients."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.vectorstore.types import VectorRecord, VectorSearchHit

logger = logging.getLogger("untold.vectorstore_client")


def vec_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in vector) + "]"


def pgvector_available(db: Session) -> bool:
    try:
        row = db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).first()
        return row is not None
    except Exception:
        return False


def pgvector_ensure_collection(db: Session, collection: str, dimension: int) -> None:
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    db.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS vector_store_documents (
                id SERIAL PRIMARY KEY,
                collection VARCHAR(128) NOT NULL,
                document_id VARCHAR(128) NOT NULL,
                content TEXT NOT NULL,
                embedding vector({dimension}) NOT NULL,
                metadata JSONB DEFAULT '{{}}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(collection, document_id)
            )
            """
        )
    )
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_vector_store_documents_collection "
            "ON vector_store_documents (collection)"
        )
    )
    db.commit()


def pgvector_upsert(db: Session, collection: str, records: list[VectorRecord]) -> int:
    count = 0
    for record in records:
        db.execute(
            text(
                """
                INSERT INTO vector_store_documents (collection, document_id, content, embedding, metadata)
                VALUES (:collection, :document_id, :content, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
                ON CONFLICT (collection, document_id) DO UPDATE SET
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata
                """
            ),
            {
                "collection": collection,
                "document_id": record.id,
                "content": record.text,
                "embedding": vec_literal(record.vector),
                "metadata": json.dumps(record.metadata or {}),
            },
        )
        count += 1
    db.commit()
    return count


def pgvector_search(
    db: Session,
    collection: str,
    vector: list[float],
    top_k: int,
) -> list[VectorSearchHit]:
    rows = db.execute(
        text(
            """
            SELECT document_id, content, metadata,
                   1 - (embedding <=> CAST(:query AS vector)) AS score
            FROM vector_store_documents
            WHERE collection = :collection
            ORDER BY embedding <=> CAST(:query AS vector)
            LIMIT :top_k
            """
        ),
        {"collection": collection, "query": vec_literal(vector), "top_k": top_k},
    ).mappings()
    hits: list[VectorSearchHit] = []
    for row in rows:
        meta = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"] or "{}")
        hits.append(
            VectorSearchHit(
                id=row["document_id"],
                text=row["content"],
                score=float(row["score"] or 0.0),
                metadata=meta,
            )
        )
    return hits


def pinecone_upsert(*, host: str, api_key: str, records: list[VectorRecord], namespace: str) -> int:
    vectors = [
        {
            "id": r.id,
            "values": r.vector,
            "metadata": {"text": r.text, **(r.metadata or {})},
        }
        for r in records
    ]
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{host.rstrip('/')}/vectors/upsert",
            headers={"Api-Key": api_key, "Content-Type": "application/json"},
            json={"vectors": vectors, "namespace": namespace},
        )
        resp.raise_for_status()
    return len(records)


def pinecone_search(
    *,
    host: str,
    api_key: str,
    vector: list[float],
    top_k: int,
    namespace: str,
) -> list[VectorSearchHit]:
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{host.rstrip('/')}/query",
            headers={"Api-Key": api_key, "Content-Type": "application/json"},
            json={"vector": vector, "topK": top_k, "includeMetadata": True, "namespace": namespace},
        )
        resp.raise_for_status()
        matches = resp.json().get("matches") or []
    hits: list[VectorSearchHit] = []
    for match in matches:
        meta = match.get("metadata") or {}
        hits.append(
            VectorSearchHit(
                id=str(match.get("id")),
                text=str(meta.get("text", "")),
                score=float(match.get("score") or 0.0),
                metadata=meta,
            )
        )
    return hits


def qdrant_ensure_collection(*, url: str, api_key: str | None, collection: str, dimension: int) -> None:
    headers = _qdrant_headers(api_key)
    payload = {"vectors": {"size": dimension, "distance": "Cosine"}}
    with httpx.Client(timeout=30.0) as client:
        resp = client.put(f"{url.rstrip('/')}/collections/{collection}", headers=headers, json=payload)
        if resp.status_code not in (200, 201, 409):
            resp.raise_for_status()


def qdrant_upsert(*, url: str, api_key: str | None, collection: str, records: list[VectorRecord]) -> int:
    headers = _qdrant_headers(api_key)
    points = [
        {"id": r.id, "vector": r.vector, "payload": {"text": r.text, **(r.metadata or {})}}
        for r in records
    ]
    with httpx.Client(timeout=60.0) as client:
        resp = client.put(
            f"{url.rstrip('/')}/collections/{collection}/points",
            headers=headers,
            json={"points": points},
        )
        resp.raise_for_status()
    return len(records)


def qdrant_search(
    *,
    url: str,
    api_key: str | None,
    collection: str,
    vector: list[float],
    top_k: int,
) -> list[VectorSearchHit]:
    headers = _qdrant_headers(api_key)
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{url.rstrip('/')}/collections/{collection}/points/search",
            headers=headers,
            json={"vector": vector, "limit": top_k, "with_payload": True},
        )
        resp.raise_for_status()
        result = resp.json().get("result") or []
    hits: list[VectorSearchHit] = []
    for item in result:
        payload = item.get("payload") or {}
        hits.append(
            VectorSearchHit(
                id=str(item.get("id")),
                text=str(payload.get("text", "")),
                score=float(item.get("score") or 0.0),
                metadata=payload,
            )
        )
    return hits


def weaviate_upsert(*, url: str, api_key: str | None, collection: str, records: list[VectorRecord]) -> int:
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"
    with httpx.Client(timeout=60.0) as client:
        for record in records:
            body = {
                "class": "UntoldDocument",
                "properties": {
                    "collection": collection,
                    "content": record.text,
                    "document_id": record.id,
                    **(record.metadata or {}),
                },
                "vector": record.vector,
            }
            resp = client.post(f"{url.rstrip('/')}/v1/objects", headers=headers, json=body)
            resp.raise_for_status()
    return len(records)


def weaviate_search(
    *,
    url: str,
    api_key: str | None,
    collection: str,
    vector: list[float],
    top_k: int,
) -> list[VectorSearchHit]:
    headers = _auth_headers(api_key)
    headers["Content-Type"] = "application/json"
    gql = {
        "query": (
            "{ Get { UntoldDocument("
            f'where: {{path: ["collection"], operator: Equal, valueText: "{collection}"}}, '
            f"nearVector: {{vector: {json.dumps(vector)}}}, limit: {top_k}"
            ") { document_id content collection _additional { distance } } } }"
        )
    }
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(f"{url.rstrip('/')}/v1/graphql", headers=headers, json=gql)
        resp.raise_for_status()
        docs = (((resp.json().get("data") or {}).get("Get") or {}).get("UntoldDocument")) or []
    hits: list[VectorSearchHit] = []
    for doc in docs:
        distance = float((doc.get("_additional") or {}).get("distance") or 1.0)
        hits.append(
            VectorSearchHit(
                id=str(doc.get("document_id")),
                text=str(doc.get("content", "")),
                score=max(0.0, 1.0 - distance),
                metadata={"collection": doc.get("collection")},
            )
        )
    return hits


def milvus_upsert(
    *,
    uri: str,
    token: str | None,
    collection: str,
    records: list[VectorRecord],
) -> int:
    headers = _auth_headers(token)
    headers["Content-Type"] = "application/json"
    data = [
        {
            "id": r.id,
            "vector": r.vector,
            "text": r.text,
            "collection": collection,
            **(r.metadata or {}),
        }
        for r in records
    ]
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{uri.rstrip('/')}/v2/vectordb/entities/insert",
            headers=headers,
            json={"collectionName": collection, "data": data},
        )
        resp.raise_for_status()
    return len(records)


def milvus_search(
    *,
    uri: str,
    token: str | None,
    collection: str,
    vector: list[float],
    top_k: int,
) -> list[VectorSearchHit]:
    headers = _auth_headers(token)
    headers["Content-Type"] = "application/json"
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{uri.rstrip('/')}/v2/vectordb/entities/search",
            headers=headers,
            json={
                "collectionName": collection,
                "data": [vector],
                "annsField": "vector",
                "limit": top_k,
                "outputFields": ["id", "text", "collection"],
            },
        )
        resp.raise_for_status()
        rows = resp.json().get("data") or []
    hits: list[VectorSearchHit] = []
    for row in rows:
        hits.append(
            VectorSearchHit(
                id=str(row.get("id")),
                text=str(row.get("text", "")),
                score=float(row.get("distance", row.get("score", 0.0)) or 0.0),
                metadata=row,
            )
        )
    return hits


def chroma_get_or_create_collection(*, url: str, api_key: str | None, collection: str) -> str:
    headers = _auth_headers(api_key)
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{url.rstrip('/')}/api/v1/collections",
            headers=headers,
            json={"name": collection},
        )
        if resp.status_code == 409:
            resp = client.get(f"{url.rstrip('/')}/api/v1/collections/{collection}", headers=headers)
        resp.raise_for_status()
        payload = resp.json()
    return payload.get("id") or collection


def chroma_upsert(
    *,
    url: str,
    api_key: str | None,
    collection: str,
    records: list[VectorRecord],
) -> int:
    headers = _auth_headers(api_key)
    collection_id = chroma_get_or_create_collection(url=url, api_key=api_key, collection=collection)
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{url.rstrip('/')}/api/v1/collections/{collection_id}/add",
            headers=headers,
            json={
                "ids": [r.id for r in records],
                "documents": [r.text for r in records],
                "embeddings": [r.vector for r in records],
                "metadatas": [r.metadata or {} for r in records],
            },
        )
        resp.raise_for_status()
    return len(records)


def chroma_search(
    *,
    url: str,
    api_key: str | None,
    collection: str,
    vector: list[float],
    top_k: int,
) -> list[VectorSearchHit]:
    headers = _auth_headers(api_key)
    collection_id = chroma_get_or_create_collection(url=url, api_key=api_key, collection=collection)
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{url.rstrip('/')}/api/v1/collections/{collection_id}/query",
            headers=headers,
            json={
                "query_embeddings": [vector],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"],
            },
        )
        resp.raise_for_status()
        data = resp.json()
    ids = (data.get("ids") or [[]])[0]
    docs = (data.get("documents") or [[]])[0]
    metas = (data.get("metadatas") or [[]])[0]
    dists = (data.get("distances") or [[]])[0]
    hits: list[VectorSearchHit] = []
    for i, doc_id in enumerate(ids):
        distance = float(dists[i]) if i < len(dists) else 0.0
        hits.append(
            VectorSearchHit(
                id=str(doc_id),
                text=str(docs[i] if i < len(docs) else ""),
                score=max(0.0, 1.0 - distance),
                metadata=metas[i] if i < len(metas) else {},
            )
        )
    return hits


def _auth_headers(api_key: str | None) -> dict[str, str]:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def _qdrant_headers(api_key: str | None) -> dict[str, str]:
    if not api_key:
        return {}
    return {"api-key": api_key}
