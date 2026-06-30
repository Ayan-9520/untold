"""Add Google OAuth and Studio RBAC fields to users."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_studio_auth"
down_revision: Union[str, None] = "006_studio_platform"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("studio_role", sa.String(length=32), nullable=True))
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)
    op.create_index("ix_users_studio_role", "users", ["studio_role"])


def downgrade() -> None:
    op.drop_index("ix_users_studio_role", table_name="users")
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_column("users", "studio_role")
    op.drop_column("users", "google_id")
