"""Research Studio — workspace, bookmarks, fact-checks, versions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_research_studio"
down_revision: Union[str, None] = "008_project_management"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("research_sessions", sa.Column("workspace_content", sa.Text(), server_default="", nullable=False))
    op.add_column("research_sessions", sa.Column("content_version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("research_sessions", sa.Column("last_auto_saved_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("research_notes", sa.Column("title", sa.String(length=300), nullable=True))
    op.add_column("research_notes", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True))
    op.add_column("research_notes", sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False))

    op.add_column("research_sources", sa.Column("is_bookmarked", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("research_sources", sa.Column("excerpt", sa.Text(), nullable=True))

    op.create_table(
        "research_bookmarks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=32), server_default="gold", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_bookmarks_research_id", "research_bookmarks", ["research_id"])

    op.create_table(
        "research_fact_checks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("checked_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["checked_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["research_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_fact_checks_research_id", "research_fact_checks", ["research_id"])

    op.create_table(
        "research_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_comments_research_id", "research_comments", ["research_id"])

    op.create_table(
        "research_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("workspace_content", sa.Text(), server_default="", nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_versions_research_id", "research_versions", ["research_id"])

    op.create_table(
        "research_timeline_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("research_id", sa.Integer(), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("event_type", sa.String(length=64), server_default="milestone", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["research_id"], ["research_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_timeline_events_research_id", "research_timeline_events", ["research_id"])


def downgrade() -> None:
    op.drop_table("research_timeline_events")
    op.drop_table("research_versions")
    op.drop_table("research_comments")
    op.drop_table("research_fact_checks")
    op.drop_table("research_bookmarks")
    op.drop_column("research_sources", "excerpt")
    op.drop_column("research_sources", "is_bookmarked")
    op.drop_column("research_notes", "is_pinned")
    op.drop_column("research_notes", "updated_at")
    op.drop_column("research_notes", "title")
    op.drop_column("research_sessions", "last_auto_saved_at")
    op.drop_column("research_sessions", "content_version")
    op.drop_column("research_sessions", "workspace_content")
