"""Add organization_id to ai_generations for tenant isolation."""

from alembic import op
import sqlalchemy as sa

revision = "049_ai_generations_organization"
down_revision = "048_enterprise_compliance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_generations",
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("ix_ai_generations_organization_id", "ai_generations", ["organization_id"])
    op.execute(
        """
        UPDATE ai_generations AS g
        SET organization_id = p.organization_id
        FROM productions AS p
        WHERE g.project_id = p.id AND p.organization_id IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_ai_generations_organization_id", table_name="ai_generations")
    op.drop_column("ai_generations", "organization_id")
