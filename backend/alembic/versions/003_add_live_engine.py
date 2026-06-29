"""Add live sports engine tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_add_live_engine"
down_revision: Union[str, None] = "002_add_news_engine"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _pg_enum(name: str, *values: str) -> postgresql.ENUM:
    enum_type = postgresql.ENUM(*values, name=name)
    enum_type.create(op.get_bind(), checkfirst=True)
    return postgresql.ENUM(*values, name=name, create_type=False)


def upgrade() -> None:
    livesport = _pg_enum("livesport", "Cricket", "Football", "Tennis", "Formula 1")
    matchstatus = _pg_enum("matchstatus", "upcoming", "live", "halftime", "completed", "postponed")
    liveprovider = _pg_enum("liveprovider", "sportmonks", "sportradar", "cricapi", "manual")
    liveeventtype = _pg_enum(
        "liveeventtype",
        "goal", "wicket", "boundary", "six", "point", "lap", "incident", "card", "substitution", "default",
    )

    op.create_table(
        "live_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=True),
        sa.Column("provider", liveprovider, nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("event_name", sa.String(length=500), nullable=False),
        sa.Column("sport", livesport, nullable=False),
        sa.Column("team_home", sa.String(length=200), nullable=False),
        sa.Column("team_away", sa.String(length=200), nullable=True),
        sa.Column("score_home", sa.String(length=50), nullable=True),
        sa.Column("score_away", sa.String(length=50), nullable=True),
        sa.Column("score_display", sa.String(length=100), nullable=True),
        sa.Column("status", matchstatus, nullable=False, server_default="live"),
        sa.Column("timer", sa.String(length=50), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=1000), nullable=True),
        sa.Column("location", sa.String(length=300), nullable=True),
        sa.Column("league", sa.String(length=200), nullable=True),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_id", name="uq_live_match_provider_external"),
    )
    op.create_index(op.f("ix_live_matches_id"), "live_matches", ["id"], unique=False)
    op.create_index(op.f("ix_live_matches_slug"), "live_matches", ["slug"], unique=True)
    op.create_index(op.f("ix_live_matches_sport"), "live_matches", ["sport"], unique=False)
    op.create_index(op.f("ix_live_matches_status"), "live_matches", ["status"], unique=False)
    op.create_index(op.f("ix_live_matches_is_featured"), "live_matches", ["is_featured"], unique=False)

    op.create_table(
        "live_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("event_type", liveeventtype, nullable=False),
        sa.Column("minute_or_over", sa.String(length=30), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("external_id", sa.String(length=200), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["live_matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_live_events_match_id"), "live_events", ["match_id"], unique=False)

    op.create_table(
        "live_commentary",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("minute_or_over", sa.String(length=30), nullable=True),
        sa.Column("ai_text", sa.Text(), nullable=False),
        sa.Column("notification_text", sa.String(length=500), nullable=True),
        sa.Column("is_breaking", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["live_matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["live_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_live_commentary_match_id"), "live_commentary", ["match_id"], unique=False)

    op.create_table(
        "match_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("stats_json", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["live_matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("match_id"),
    )

    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(length=200), nullable=False),
        sa.Column("provider", liveprovider, nullable=False),
        sa.Column("sport", livesport, nullable=False),
        sa.Column("event_name", sa.String(length=500), nullable=False),
        sa.Column("team_home", sa.String(length=200), nullable=False),
        sa.Column("team_away", sa.String(length=200), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(length=300), nullable=True),
        sa.Column("status", matchstatus, nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["live_matches.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "external_id", name="uq_fixture_provider_external"),
    )

    op.create_table(
        "live_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default="in_app"),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["live_matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["live_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("live_notifications")
    op.drop_table("fixtures")
    op.drop_table("match_stats")
    op.drop_table("live_commentary")
    op.drop_table("live_events")
    op.drop_table("live_matches")

    sa.Enum(name="liveeventtype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="liveprovider").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="matchstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="livesport").drop(op.get_bind(), checkfirst=True)
