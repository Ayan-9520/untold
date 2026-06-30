"""AI Music Studio — versions table."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "023_ai_music_studio"
down_revision: Union[str, None] = "022_ai_voice_studio"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_music_versions",
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
    op.create_index("ix_ai_music_versions_generation_id", "ai_music_versions", ["generation_id"])


def downgrade() -> None:
    op.drop_index("ix_ai_music_versions_generation_id", table_name="ai_music_versions")
    op.drop_table("ai_music_versions")
