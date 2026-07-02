"""OTT platform pages, FAQ, consumer promo codes."""

from alembic import op
import sqlalchemy as sa

revision = "054_ott_platform"
down_revision = "053_newsletter"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "platform_pages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_platform_pages_slug", "platform_pages", ["slug"])

    op.create_table(
        "platform_faq",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("faq_key", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("faq_key"),
    )

    op.create_table(
        "consumer_promo_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("discount_percent", sa.Integer(), nullable=False),
        sa.Column("plan_slugs_json", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_consumer_promo_codes_code", "consumer_promo_codes", ["code"])


def downgrade() -> None:
    op.drop_index("ix_consumer_promo_codes_code", table_name="consumer_promo_codes")
    op.drop_table("consumer_promo_codes")
    op.drop_table("platform_faq")
    op.drop_index("ix_platform_pages_slug", table_name="platform_pages")
    op.drop_table("platform_pages")
