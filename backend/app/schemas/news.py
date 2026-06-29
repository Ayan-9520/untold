from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.news import NewsStatus, NewsType
from app.schemas.common import ORMBase


class NewsTagResponse(ORMBase):
    id: int
    name: str
    slug: str


class NewsCategoryResponse(ORMBase):
    id: int
    name: str
    slug: str
    description: str | None = None


class NewsListParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=50)
    sport: str | None = None
    news_type: str | None = None
    breaking: bool | None = None
    trending: bool | None = None
    search: str | None = None


class NewsArticleResponse(ORMBase):
    id: int
    slug: str
    title: str
    excerpt: str | None = None
    summary: str | None = None
    sport: str
    news_type: NewsType
    is_breaking: bool
    is_trending: bool
    thumbnail_url: str | None = None
    source_url: str | None = None
    author: str
    published_at: datetime | None = None
    views_count: int
    category: NewsCategoryResponse | None = None
    tags: list[NewsTagResponse] = []


class NewsArticleDetailResponse(NewsArticleResponse):
    content: str | None = None
    rewritten_content: str | None = None
    headline_variants: list[str] = []
    social_captions: dict[str, str] = {}
    seo_title: str | None = None
    seo_description: str | None = None
    seo_keywords: str | None = None
    status: NewsStatus


class NewsCreateRequest(BaseModel):
    title: str = Field(min_length=5, max_length=500)
    excerpt: str | None = None
    content: str | None = None
    sport: str = Field(min_length=2, max_length=80)
    news_type: NewsType = NewsType.FEATURE
    is_breaking: bool = False
    is_trending: bool = False
    thumbnail_url: str | None = None
    source_url: str | None = None
    author: str = "UNTOLD Editorial"
    category_slug: str | None = None
    tag_slugs: list[str] = []
    auto_process_ai: bool = True


class NewsPublishRequest(BaseModel):
    news_id: int = Field(gt=0)
    approve: bool = True


class NewsPublishResponse(BaseModel):
    message: str
    article: NewsArticleDetailResponse


class NewsFetchResponse(BaseModel):
    message: str
    task_id: str | None = None
    sources_queued: int = 0
