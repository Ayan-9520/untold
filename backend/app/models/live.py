"""Live sports engine ORM models."""

from datetime import datetime
import enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LiveSport(str, enum.Enum):
    CRICKET = "Cricket"
    FOOTBALL = "Football"
    TENNIS = "Tennis"
    FORMULA_1 = "Formula 1"


class MatchStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    HALFTIME = "halftime"
    COMPLETED = "completed"
    POSTPONED = "postponed"


class LiveProvider(str, enum.Enum):
    SPORTMONKS = "sportmonks"
    SPORTRADAR = "sportradar"
    CRICAPI = "cricapi"
    MANUAL = "manual"


class LiveEventType(str, enum.Enum):
    GOAL = "goal"
    WICKET = "wicket"
    BOUNDARY = "boundary"
    SIX = "six"
    POINT = "point"
    LAP = "lap"
    INCIDENT = "incident"
    CARD = "card"
    SUBSTITUTION = "substitution"
    DEFAULT = "default"


class LiveMatch(Base):
    __tablename__ = "live_matches"
    __table_args__ = (UniqueConstraint("provider", "external_id", name="uq_live_match_provider_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    provider: Mapped[LiveProvider] = mapped_column(Enum(LiveProvider), default=LiveProvider.MANUAL, nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    event_name: Mapped[str] = mapped_column(String(500), nullable=False)
    sport: Mapped[LiveSport] = mapped_column(Enum(LiveSport), nullable=False, index=True)
    team_home: Mapped[str] = mapped_column(String(200), nullable=False)
    team_away: Mapped[str | None] = mapped_column(String(200), nullable=True)
    score_home: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score_away: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score_display: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.LIVE, nullable=False, index=True)
    timer: Mapped[str | None] = mapped_column(String(50), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    location: Mapped[str | None] = mapped_column(String(300), nullable=True)
    league: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    events: Mapped[list["LiveEvent"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    commentary: Mapped[list["LiveCommentary"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    stats: Mapped["MatchStat | None"] = relationship(back_populates="match", uselist=False, cascade="all, delete-orphan")
    notifications: Mapped[list["LiveNotification"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    fixture: Mapped["Fixture | None"] = relationship(back_populates="match", uselist=False)


class LiveEvent(Base):
    __tablename__ = "live_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("live_matches.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[LiveEventType] = mapped_column(Enum(LiveEventType), default=LiveEventType.DEFAULT, nullable=False)
    minute_or_over: Mapped[str | None] = mapped_column(String(30), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match: Mapped[LiveMatch] = relationship(back_populates="events")
    commentary_entries: Mapped[list["LiveCommentary"]] = relationship(back_populates="event")


class LiveCommentary(Base):
    __tablename__ = "live_commentary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("live_matches.id", ondelete="CASCADE"), index=True, nullable=False)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("live_events.id", ondelete="SET NULL"), index=True, nullable=True)
    minute_or_over: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ai_text: Mapped[str] = mapped_column(Text, nullable=False)
    notification_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    match: Mapped[LiveMatch] = relationship(back_populates="commentary")
    event: Mapped[LiveEvent | None] = relationship(back_populates="commentary_entries")


class MatchStat(Base):
    __tablename__ = "match_stats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("live_matches.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    stats_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    match: Mapped[LiveMatch] = relationship(back_populates="stats")


class Fixture(Base):
    __tablename__ = "fixtures"
    __table_args__ = (UniqueConstraint("provider", "external_id", name="uq_fixture_provider_external"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    provider: Mapped[LiveProvider] = mapped_column(Enum(LiveProvider), nullable=False)
    sport: Mapped[LiveSport] = mapped_column(Enum(LiveSport), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(500), nullable=False)
    team_home: Mapped[str] = mapped_column(String(200), nullable=False)
    team_away: Mapped[str | None] = mapped_column(String(200), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    venue: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.UPCOMING, nullable=False)
    match_id: Mapped[int | None] = mapped_column(ForeignKey("live_matches.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match: Mapped[LiveMatch | None] = relationship(back_populates="fixture")


class LiveNotification(Base):
    __tablename__ = "live_notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("live_matches.id", ondelete="CASCADE"), index=True, nullable=False)
    event_id: Mapped[int | None] = mapped_column(ForeignKey("live_events.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="in_app", nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match: Mapped[LiveMatch] = relationship(back_populates="notifications")
