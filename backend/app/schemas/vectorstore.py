"""Vector store API schemas."""

from pydantic import BaseModel, Field


class VectorRecordInput(BaseModel):
    id: str
    text: str
    vector: list[float]
    metadata: dict = Field(default_factory=dict)


class VectorUpsertBody(BaseModel):
    collection: str
    records: list[VectorRecordInput]
    dimension: int | None = None
    provider: str | None = None


class VectorSearchBody(BaseModel):
    collection: str
    vector: list[float]
    top_k: int = Field(default=10, ge=1, le=100)
    filter: dict | None = None
    provider: str | None = None


class VectorSearchHitResponse(BaseModel):
    id: str
    text: str
    score: float
    metadata: dict = Field(default_factory=dict)


class VectorUpsertResponse(BaseModel):
    upserted: int
    collection: str
    provider: str
    meta: dict = Field(default_factory=dict)


class VectorSearchResponse(BaseModel):
    hits: list[VectorSearchHitResponse]
    collection: str
    provider: str
    meta: dict = Field(default_factory=dict)
