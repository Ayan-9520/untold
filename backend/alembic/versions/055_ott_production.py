"""OTT production: viewer profiles, video playback metadata, live reminders."""

from alembic import op
import sqlalchemy as sa

revision = "055_ott_production"
down_revision = "054_ott_platform"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "viewer_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("avatar", sa.String(length=20), server_default="🎬", nullable=False),
        sa.Column("is_kids", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("pin_hash", sa.String(length=255), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_viewer_profiles_user_id", "viewer_profiles", ["user_id"])

    op.add_column("videos", sa.Column("subtitle_url", sa.String(length=1000), nullable=True))
    op.add_column("videos", sa.Column("intro_end_seconds", sa.Integer(), nullable=True))
    op.add_column("videos", sa.Column("next_video_id", sa.Integer(), nullable=True))

    op.create_table(
        "live_event_reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.String(length=80), nullable=False),
        sa.Column("match_title", sa.String(length=255), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "match_id", name="uq_live_reminder_user_match"),
    )

    op.add_column("users", sa.Column("preferences_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "preferences_json")
    op.drop_table("live_event_reminders")
    op.drop_column("videos", "next_video_id")
    op.drop_column("videos", "intro_end_seconds")
    op.drop_column("videos", "subtitle_url")
    op.drop_index("ix_viewer_profiles_user_id", table_name="viewer_profiles")
    op.drop_table("viewer_profiles")
