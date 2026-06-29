"""Add news engine tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_add_news_engine"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pg_enum(name: str, *values: str) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name)
    enum_type.create(op.get_bind(), checkfirst=True)
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    newstype = _pg_enum("newstype", "breaking", "match_update", "feature", "exclusive")
    newsstatus = _pg_enum("newsstatus", "draft", "pending_review", "published", "archived")
    newssourcetype = _pg_enum("newssourcetype", "rss", "sportmonks", "sportradar", "cricapi", "manual")

    op.create_table(
        "news_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_news_categories_id"), "news_categories", ["id"], unique=False)
    op.create_index(op.f("ix_news_categories_slug"), "news_categories", ["slug"], unique=True)

    op.create_table(
        "news_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_news_tags_id"), "news_tags", ["id"], unique=False)
    op.create_index(op.f("ix_news_tags_slug"), "news_tags", ["slug"], unique=True)

    op.create_table(
        "news_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("source_type", newssourcetype, nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("sport", sa.String(length=80), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("fetch_interval_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_news_sources_id"), "news_sources", ["id"], unique=False)
    op.create_index(op.f("ix_news_sources_source_type"), "news_sources", ["source_type"], unique=False)
    op.create_index(op.f("ix_news_sources_sport"), "news_sources", ["sport"], unique=False)

    op.create_table(
        "news",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=500), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("rewritten_content", sa.Text(), nullable=True),
        sa.Column("headline_variants_json", sa.Text(), nullable=True),
        sa.Column("social_captions_json", sa.Text(), nullable=True),
        sa.Column("seo_title", sa.String(length=200), nullable=True),
        sa.Column("seo_description", sa.String(length=500), nullable=True),
        sa.Column("seo_keywords", sa.String(length=500), nullable=True),
        sa.Column("sport", sa.String(length=80), nullable=False),
        sa.Column("news_type", newstype, nullable=False, server_default="feature"),
        sa.Column("status", newsstatus, nullable=False, server_default="draft"),
        sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_trending", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("external_id", sa.String(length=500), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=False, server_default="UNTOLD Editorial"),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["news_categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_id"], ["news_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_news_source_external"),
    )
    op.create_index(op.f("ix_news_external_id"), "news", ["external_id"], unique=False)
    op.create_index(op.f("ix_news_id"), "news", ["id"], unique=False)
    op.create_index(op.f("ix_news_is_breaking"), "news", ["is_breaking"], unique=False)
    op.create_index(op.f("ix_news_is_trending"), "news", ["is_trending"], unique=False)
    op.create_index(op.f("ix_news_news_type"), "news", ["news_type"], unique=False)
    op.create_index(op.f("ix_news_published_at"), "news", ["published_at"], unique=False)
    op.create_index(op.f("ix_news_slug"), "news", ["slug"], unique=True)
    op.create_index(op.f("ix_news_sport"), "news", ["sport"], unique=False)
    op.create_index(op.f("ix_news_status"), "news", ["status"], unique=False)
    op.create_index(op.f("ix_news_title"), "news", ["title"], unique=False)
    op.create_index(op.f("ix_news_category_id"), "news", ["category_id"], unique=False)
    op.create_index(op.f("ix_news_source_id"), "news", ["source_id"], unique=False)

    op.create_table(
        "news_article_tags",
        sa.Column("news_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["news_id"], ["news.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["news_tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("news_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("news_article_tags")
    op.drop_table("news")
    op.drop_table("news_sources")
    op.drop_table("news_tags")
    op.drop_table("news_categories")

    sa.Enum(name="newssourcetype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="newsstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="newstype").drop(op.get_bind(), checkfirst=True)
