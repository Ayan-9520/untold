from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class CategoryResponse(ORMBase):
    id: int
    name: str
    slug: str
    description: str | None
    created_at: datetime


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str | None = None


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
