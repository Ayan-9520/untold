"""Plugin SDK — marketplace, installations, events."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "035_plugin_sdk"
down_revision: Union[str, None] = "034_enterprise_collaboration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plugin_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(length=16), server_default="🧩", nullable=False),
        sa.Column("category", sa.String(length=32), server_default="integration", nullable=False),
        sa.Column("author", sa.String(length=120), server_default="UNTOLD", nullable=False),
        sa.Column("author_url", sa.String(length=500), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="published", nullable=False),
        sa.Column("current_version_id", sa.Integer(), nullable=True),
        sa.Column("manifest", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("default_settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("available_permissions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("backend_entry", sa.String(length=200), nullable=True),
        sa.Column("frontend_entry", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_plugin_definition_slug"),
    )
    op.create_index("ix_plugin_definitions_category", "plugin_definitions", ["category"])

    op.create_table(
        "plugin_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plugin_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("manifest", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("settings_schema", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("default_settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("changelog", sa.String(length=500), nullable=True),
        sa.Column("release_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugin_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plugin_id", "version", name="uq_plugin_version"),
    )
    op.create_index("ix_plugin_versions_plugin_id", "plugin_versions", ["plugin_id"])

    op.create_table(
        "plugin_installations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plugin_id", sa.Integer(), nullable=False),
        sa.Column("installed_version_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("granted_permissions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("status", sa.String(length=32), server_default="active", nullable=False),
        sa.Column("installed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("last_enabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugin_definitions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["installed_version_id"], ["plugin_versions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "plugin_id", name="uq_plugin_installation_user_plugin"),
    )
    op.create_index("ix_plugin_installations_user_id", "plugin_installations", ["user_id"])
    op.create_index("ix_plugin_installations_plugin_id", "plugin_installations", ["plugin_id"])

    op.create_table(
        "plugin_installation_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("from_version", sa.Integer(), nullable=True),
        sa.Column("to_version", sa.Integer(), nullable=True),
        sa.Column("settings_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("performed_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["plugin_installations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plugin_installation_history_installation_id", "plugin_installation_history", ["installation_id"])

    op.create_table(
        "plugin_event_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("installation_id", sa.Integer(), nullable=True),
        sa.Column("plugin_slug", sa.String(length=64), nullable=False),
        sa.Column("event_name", sa.String(length=120), nullable=False),
        sa.Column("hook_name", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="success", nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["installation_id"], ["plugin_installations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_plugin_event_log_event_name", "plugin_event_log", ["event_name"])
    op.create_index("ix_plugin_event_log_plugin_slug", "plugin_event_log", ["plugin_slug"])

    op.create_foreign_key(
        "fk_plugin_definitions_current_version",
        "plugin_definitions",
        "plugin_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_plugin_definitions_current_version", "plugin_definitions", type_="foreignkey")
    op.drop_table("plugin_event_log")
    op.drop_table("plugin_installation_history")
    op.drop_table("plugin_installations")
    op.drop_table("plugin_versions")
    op.drop_table("plugin_definitions")
