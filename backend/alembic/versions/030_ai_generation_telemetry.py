"""AI generation telemetry — tokens, latency, cost, model."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "030_ai_generation_telemetry"
down_revision: Union[str, None] = "029_workflow_run_controls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ai_generations", sa.Column("model", sa.String(length=128), nullable=True))
    op.add_column("ai_generations", sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False))
    op.add_column("ai_generations", sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False))
    op.add_column("ai_generations", sa.Column("latency_ms", sa.Integer(), nullable=True))
    op.add_column("ai_generations", sa.Column("cost_usd", sa.Numeric(12, 6), nullable=True))
    op.add_column("ai_generations", sa.Column("failure_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("ai_generations", sa.Column("approval_status", sa.String(length=32), server_default="none", nullable=False))
    op.add_column("ai_generations", sa.Column("prompt_version", sa.String(length=64), nullable=True))
    op.add_column("ai_generations", sa.Column("temperature", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("ai_generations", "temperature")
    op.drop_column("ai_generations", "prompt_version")
    op.drop_column("ai_generations", "approval_status")
    op.drop_column("ai_generations", "failure_count")
    op.drop_column("ai_generations", "cost_usd")
    op.drop_column("ai_generations", "latency_ms")
    op.drop_column("ai_generations", "output_tokens")
    op.drop_column("ai_generations", "input_tokens")
    op.drop_column("ai_generations", "model")
