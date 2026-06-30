"""Publishing CMS — visibility, SEO, thumbnails, job retries."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "015_publishing_cms"
down_revision: Union[str, None] = "014_timeline_editor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("productions", sa.Column("visibility", sa.String(length=32), server_default="draft", nullable=False))
    op.add_column("productions", sa.Column("thumbnail_url", sa.String(length=1000), nullable=True))

    op.add_column("publish_jobs", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column("publish_jobs", sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("publish_jobs", sa.Column("approval_status", sa.String(length=32), server_default="pending", nullable=False))
    op.add_column("publish_jobs", sa.Column("approved_by_id", sa.Integer(), nullable=True))
    op.add_column("publish_jobs", sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("publish_jobs", sa.Column("thumbnail_url", sa.String(length=1000), nullable=True))
    op.add_column("publish_jobs", sa.Column("seo_title", sa.String(length=500), nullable=True))
    op.add_column("publish_jobs", sa.Column("seo_description", sa.Text(), nullable=True))
    op.add_column("publish_jobs", sa.Column("seo_keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_foreign_key(
        "fk_publish_jobs_approved_by",
        "publish_jobs",
        "users",
        ["approved_by_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_publish_jobs_approved_by", "publish_jobs", type_="foreignkey")
    op.drop_column("publish_jobs", "seo_keywords")
    op.drop_column("publish_jobs", "seo_description")
    op.drop_column("publish_jobs", "seo_title")
    op.drop_column("publish_jobs", "thumbnail_url")
    op.drop_column("publish_jobs", "approved_at")
    op.drop_column("publish_jobs", "approved_by_id")
    op.drop_column("publish_jobs", "approval_status")
    op.drop_column("publish_jobs", "retry_count")
    op.drop_column("publish_jobs", "error_message")
    op.drop_column("productions", "thumbnail_url")
    op.drop_column("productions", "visibility")
