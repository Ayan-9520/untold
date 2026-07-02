"""AI Cost Intelligence — cost event ledger migration."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "041_ai_cost_intelligence"
down_revision: Union[str, None] = "040_enterprise_billing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    modality = postgresql.ENUM(
        "tokens",
        "image",
        "video",
        "voice",
        "music",
        "translation",
        name="aicostmodality",
        create_type=True,
    )
    modality.create(op.get_bind(), checkfirst=True)
    modality_col = postgresql.ENUM(
        "tokens",
        "image",
        "video",
        "voice",
        "music",
        "translation",
        name="aicostmodality",
        create_type=False,
    )

    op.create_table(
        "ai_cost_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("generation_id", sa.Integer(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=64), nullable=False),
        sa.Column("modality", modality_col, server_default="tokens", nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("cost_usd", sa.Float(), server_default="0", nullable=False),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("units", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("cache_hit", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["generation_id"], ["ai_generations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["productions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_cost_events_org_created", "ai_cost_events", ["organization_id", "created_at"])
    op.create_index("ix_ai_cost_events_module_created", "ai_cost_events", ["module", "created_at"])
    op.create_index("ix_ai_cost_events_modality", "ai_cost_events", ["modality"])


def downgrade() -> None:
    op.drop_index("ix_ai_cost_events_modality", table_name="ai_cost_events")
    op.drop_index("ix_ai_cost_events_module_created", table_name="ai_cost_events")
    op.drop_index("ix_ai_cost_events_org_created", table_name="ai_cost_events")
    op.drop_table("ai_cost_events")
    op.execute("DROP TYPE IF EXISTS aicostmodality")
