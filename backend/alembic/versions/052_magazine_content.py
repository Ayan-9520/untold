"""Magazine edition content and page count."""

from alembic import op
import sqlalchemy as sa

revision = "052_magazine_content"
down_revision = "051_auth_contact"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("magazines", sa.Column("content_json", sa.Text(), nullable=True))
    op.add_column("magazines", sa.Column("page_count", sa.Integer(), server_default="48", nullable=False))


def downgrade() -> None:
    op.drop_column("magazines", "page_count")
    op.drop_column("magazines", "content_json")
