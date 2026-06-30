"""Asset Library — folders, collections, versions, soft delete."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013_asset_library"
down_revision: Union[str, None] = "012_ai_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("studio_assets", sa.Column("title", sa.String(length=500), nullable=True))
    op.add_column("studio_assets", sa.Column("folder", sa.String(length=32), server_default="images", nullable=False))
    op.add_column(
        "studio_assets",
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
    )
    op.add_column("studio_assets", sa.Column("is_favorite", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("studio_assets", sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("studio_assets", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("studio_assets", sa.Column("version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("studio_assets", sa.Column("cloud_provider", sa.String(length=32), server_default="local", nullable=False))
    op.add_column("studio_assets", sa.Column("preview_url", sa.String(length=2000), nullable=True))
    op.add_column(
        "studio_assets",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.add_column("studio_assets", sa.Column("collection_id", sa.Integer(), nullable=True))

    op.create_table(
        "asset_collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(length=32), server_default="gold", nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asset_collections_project_id", "asset_collections", ["project_id"])

    op.create_foreign_key(
        "fk_studio_assets_collection_id",
        "studio_assets",
        "asset_collections",
        ["collection_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "asset_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column("r2_key", sa.String(length=1000), nullable=False),
        sa.Column("url", sa.String(length=2000), nullable=True),
        sa.Column("size_bytes", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["studio_assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asset_versions_asset_id", "asset_versions", ["asset_id"])

    op.create_table(
        "asset_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(length=32), nullable=True),
        sa.Column("permission", sa.String(length=32), server_default="read", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["asset_id"], ["studio_assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asset_permissions_asset_id", "asset_permissions", ["asset_id"])

    op.create_index("ix_studio_assets_folder", "studio_assets", ["folder"])
    op.create_index("ix_studio_assets_is_deleted", "studio_assets", ["is_deleted"])


def downgrade() -> None:
    op.drop_index("ix_studio_assets_is_deleted", table_name="studio_assets")
    op.drop_index("ix_studio_assets_folder", table_name="studio_assets")
    op.drop_table("asset_permissions")
    op.drop_index("ix_asset_versions_asset_id", table_name="asset_versions")
    op.drop_table("asset_versions")
    op.drop_constraint("fk_studio_assets_collection_id", "studio_assets", type_="foreignkey")
    op.drop_index("ix_asset_collections_project_id", table_name="asset_collections")
    op.drop_table("asset_collections")
    op.drop_column("studio_assets", "collection_id")
    op.drop_column("studio_assets", "updated_at")
    op.drop_column("studio_assets", "preview_url")
    op.drop_column("studio_assets", "cloud_provider")
    op.drop_column("studio_assets", "version")
    op.drop_column("studio_assets", "deleted_at")
    op.drop_column("studio_assets", "is_deleted")
    op.drop_column("studio_assets", "is_favorite")
    op.drop_column("studio_assets", "tags")
    op.drop_column("studio_assets", "folder")
    op.drop_column("studio_assets", "title")
