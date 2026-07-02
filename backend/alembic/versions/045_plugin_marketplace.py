"""Plugin marketplace — ratings, org scope, semver labels, documentation."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "045_plugin_marketplace"
down_revision: Union[str, None] = "044_business_intelligence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("plugin_definitions", sa.Column("documentation_url", sa.String(length=500), nullable=True))
    op.add_column("plugin_definitions", sa.Column("install_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("plugin_definitions", sa.Column("average_rating", sa.Float(), server_default="0", nullable=False))
    op.add_column("plugin_definitions", sa.Column("rating_count", sa.Integer(), server_default="0", nullable=False))

    op.add_column("plugin_versions", sa.Column("version_label", sa.String(length=32), server_default="1.0.0", nullable=False))

    op.add_column("plugin_installations", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index("ix_plugin_installations_organization_id", "plugin_installations", ["organization_id"])
    op.create_foreign_key(
        "fk_plugin_installations_organization",
        "plugin_installations",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "plugin_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plugin_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["plugin_id"], ["plugin_definitions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plugin_id", "user_id", name="uq_plugin_rating_user"),
    )
    op.create_index("ix_plugin_ratings_plugin", "plugin_ratings", ["plugin_id"])


def downgrade() -> None:
    op.drop_table("plugin_ratings")
    op.drop_constraint("fk_plugin_installations_organization", "plugin_installations", type_="foreignkey")
    op.drop_index("ix_plugin_installations_organization_id", table_name="plugin_installations")
    op.drop_column("plugin_installations", "organization_id")
    op.drop_column("plugin_versions", "version_label")
    op.drop_column("plugin_definitions", "rating_count")
    op.drop_column("plugin_definitions", "average_rating")
    op.drop_column("plugin_definitions", "install_count")
    op.drop_column("plugin_definitions", "documentation_url")
