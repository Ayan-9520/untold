"""AI Image Studio — favorites, collections, versions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "020_ai_image_studio"
down_revision: Union[str, None] = "019_storyboard_ai_generator"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ai_generations", sa.Column("parent_generation_id", sa.Integer(), nullable=True))
    op.add_column("ai_generations", sa.Column("is_favorite", sa.Boolean(), server_default="false", nullable=False))
    op.create_foreign_key(
        "fk_ai_generations_parent",
        "ai_generations",
        "ai_generations",
        ["parent_generation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_ai_generations_parent", "ai_generations", ["parent_generation_id"])
    op.create_index("ix_ai_generations_is_favorite", "ai_generations", ["is_favorite"])

    op.create_table(
        "ai_image_collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ai_image_collection_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("generation_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["collection_id"], ["ai_image_collections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["generation_id"], ["ai_generations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_image_collection_items_collection", "ai_image_collection_items", ["collection_id"])

    op.create_table(
        "ai_image_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("generation_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("result_url", sa.String(length=2000), nullable=True),
        sa.Column("r2_key", sa.String(length=1000), nullable=True),
        sa.Column("output_meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["generation_id"], ["ai_generations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_image_versions_generation", "ai_image_versions", ["generation_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_image_versions_generation", table_name="ai_image_versions")
    op.drop_table("ai_image_versions")
    op.drop_index("ix_ai_image_collection_items_collection", table_name="ai_image_collection_items")
    op.drop_table("ai_image_collection_items")
    op.drop_table("ai_image_collections")
    op.drop_index("ix_ai_generations_is_favorite", table_name="ai_generations")
    op.drop_index("ix_ai_generations_parent", table_name="ai_generations")
    op.drop_constraint("fk_ai_generations_parent", "ai_generations", type_="foreignkey")
    op.drop_column("ai_generations", "is_favorite")
    op.drop_column("ai_generations", "parent_generation_id")
