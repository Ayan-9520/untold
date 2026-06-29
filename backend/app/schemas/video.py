from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.category import CategoryResponse
from app.schemas.common import ORMBase


class VideoResponse(ORMBase):
    id: int
    title: str
    slug: str
    description: str | None
    category_id: int | None
    category: CategoryResponse | None = None
    duration: str | None
    duration_seconds: int | None
    year: int | None
    rating: str | None
    image_url: str | None
    hero_image_url: str | None
    video_url: str | None
    video_type: str
    is_featured: bool
    is_trending: bool
    views_count: int
    is_active: bool
    created_at: datetime


class VideoListParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    category: str | None = None
    video_type: str | None = None
    featured: bool | None = None
    trending: bool | None = None
    search: str | None = None


class VideoCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    slug: str = Field(min_length=1, max_length=500)
    description: str | None = None
    category_id: int | None = None
    duration: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    rating: str | None = None
    image_url: str | None = None
    hero_image_url: str | None = None
    video_url: str | None = None
    video_type: str = "documentary"
    is_featured: bool = False
    is_trending: bool = False


class VideoUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    category_id: int | None = None
    duration: str | None = None
    duration_seconds: int | None = None
    year: int | None = None
    rating: str | None = None
    image_url: str | None = None
    hero_image_url: str | None = None
    video_url: str | None = None
    video_type: str | None = None
    is_featured: bool | None = None
    is_trending: bool | None = None
    is_active: bool | None = None
