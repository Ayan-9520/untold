"""News engine ORM models."""

from datetime import datetime
import enum

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NewsType(str, enum.Enum):
    BREAKING = "breaking"
    MATCH_UPDATE = "match_update"
    FEATURE = "feature"
    EXCLUSIVE = "exclusive"


class NewsStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class NewsSourceType(str, enum.Enum):
    RSS = "rss"
    SPORTMONKS = "sportmonks"
    SPORTRADAR = "sportradar"
    CRICAPI = "cricapi"
    MANUAL = "manual"


news_article_tags = Table(
    "news_article_tags",
    Base.metadata,
    sa.Column("news_id", Integer, ForeignKey("news.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("tag_id", Integer, ForeignKey("news_tags.id", ondelete="CASCADE"), primary_key=True),
)


class NewsCategory(Base):
    __tablename__ = "news_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    articles: Mapped[list["NewsArticle"]] = relationship(back_populates="category")


class NewsTag(Base):
    __tablename__ = "news_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    articles: Mapped[list["NewsArticle"]] = relationship(
        secondary=news_article_tags,
        back_populates="tags",
    )


class NewsSource(Base):
    __tablename__ = "news_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[NewsSourceType] = mapped_column(Enum(NewsSourceType), nullable=False, index=True)
    url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    sport: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fetch_interval_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    articles: Mapped[list["NewsArticle"]] = relationship(back_populates="source")


class NewsArticle(Base):
    __tablename__ = "news"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_news_source_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    rewritten_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    headline_variants_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    social_captions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seo_keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sport: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    news_type: Mapped[NewsType] = mapped_column(
        Enum(NewsType), default=NewsType.FEATURE, nullable=False, index=True
    )
    status: Mapped[NewsStatus] = mapped_column(
        Enum(NewsStatus), default=NewsStatus.DRAFT, nullable=False, index=True
    )
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    author: Mapped[str] = mapped_column(String(255), default="UNTOLD Editorial", nullable=False)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("news_categories.id", ondelete="SET NULL"), index=True, nullable=True
    )
    source_id: Mapped[int | None] = mapped_column(
        ForeignKey("news_sources.id", ondelete="SET NULL"), index=True, nullable=True
    )

    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    ai_processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ai_metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[NewsCategory | None] = relationship(back_populates="articles")
    source: Mapped[NewsSource | None] = relationship(back_populates="articles")
    tags: Mapped[list[NewsTag]] = relationship(
        secondary=news_article_tags,
        back_populates="articles",
    )
