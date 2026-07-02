"""Magazine workflow jobs persistence."""

from alembic import op
import sqlalchemy as sa

revision = "050_magazine_jobs"
down_revision = "049_ai_generations_organization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "magazine_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("theme", sa.String(length=200), nullable=False),
        sa.Column("quarter", sa.String(length=20), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="collecting"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("steps_json", sa.Text(), nullable=True),
        sa.Column("published_issue_slug", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_magazine_jobs_external_id", "magazine_jobs", ["external_id"])


def downgrade() -> None:
    op.drop_index("ix_magazine_jobs_external_id", table_name="magazine_jobs")
    op.drop_table("magazine_jobs")
