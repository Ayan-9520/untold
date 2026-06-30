"""Add prompt versioning columns to ai_prompt_library."""

from alembic import op
import sqlalchemy as sa

revision = "038_ai_prompt_versioning"
down_revision = "037_enterprise_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ai_prompt_library",
        sa.Column("prompt_key", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "ai_prompt_library",
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
    )
    op.add_column(
        "ai_prompt_library",
        sa.Column("is_current", sa.Boolean(), server_default="true", nullable=False),
    )
    op.create_index("ix_ai_prompt_library_prompt_key", "ai_prompt_library", ["prompt_key"])
    op.create_index(
        "ix_ai_prompt_library_module_key_version",
        "ai_prompt_library",
        ["module", "prompt_key", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_ai_prompt_library_module_key_version", table_name="ai_prompt_library")
    op.drop_index("ix_ai_prompt_library_prompt_key", table_name="ai_prompt_library")
    op.drop_column("ai_prompt_library", "is_current")
    op.drop_column("ai_prompt_library", "version")
    op.drop_column("ai_prompt_library", "prompt_key")
