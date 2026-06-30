"""Agent marketplace — catalog tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "032_agent_marketplace"
down_revision: Union[str, None] = "031_workflow_platform"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "marketplace_agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(length=16), server_default="🤖", nullable=False),
        sa.Column("category", sa.String(length=32), server_default="production", nullable=False),
        sa.Column("studio_route", sa.String(length=120), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="published", nullable=False),
        sa.Column("current_version_id", sa.Integer(), nullable=True),
        sa.Column("default_config", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("available_permissions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_marketplace_agent_slug"),
    )
    op.create_index("ix_marketplace_agents_category", "marketplace_agents", ["category"])

    op.create_table(
        "marketplace_agent_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("default_config", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("config_schema", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("changelog", sa.String(length=500), nullable=True),
        sa.Column("release_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["marketplace_agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "version", name="uq_marketplace_agent_version"),
    )
    op.create_index("ix_marketplace_agent_versions_agent_id", "marketplace_agent_versions", ["agent_id"])

    op.create_table(
        "agent_installations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("installed_version_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("granted_permissions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("last_enabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["marketplace_agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["installed_version_id"], ["marketplace_agent_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "agent_id", name="uq_agent_installation_user_agent"),
    )
    op.create_index("ix_agent_installations_user_id", "agent_installations", ["user_id"])
    op.create_index("ix_agent_installations_agent_id", "agent_installations", ["agent_id"])

    op.create_table(
        "agent_installation_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("from_version", sa.Integer(), nullable=True),
        sa.Column("to_version", sa.Integer(), nullable=True),
        sa.Column("config_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("performed_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["agent_installations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_installation_history_installation_id", "agent_installation_history", ["installation_id"])

    op.create_foreign_key(
        "fk_marketplace_agents_current_version",
        "marketplace_agents",
        "marketplace_agent_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_marketplace_agents_current_version", "marketplace_agents", type_="foreignkey")
    op.drop_table("agent_installation_history")
    op.drop_table("agent_installations")
    op.drop_table("marketplace_agent_versions")
    op.drop_table("marketplace_agents")
