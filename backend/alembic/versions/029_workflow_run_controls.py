"""Workflow run approval and retry controls."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "029_workflow_run_controls"
down_revision: Union[str, None] = "028_production_pipeline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "production_pipeline_runs",
        sa.Column("requires_approval", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column(
        "production_pipeline_runs",
        sa.Column("approval_status", sa.String(length=32), server_default="none", nullable=False),
    )
    op.add_column(
        "production_pipeline_runs",
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("production_pipeline_runs", "retry_count")
    op.drop_column("production_pipeline_runs", "approval_status")
    op.drop_column("production_pipeline_runs", "requires_approval")
