"""UNTOLD Studio — research models."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, StrEnum
from app.domain.studio.enums import (
    AIGenerationModule,
    AIGenerationStatus,
    ApprovalStatus,
    AssetType,
    PublishPlatform,
    PublishingStatus,
    ScriptStyle,
    StudioRole,
    TaskPriority,
    TaskStatus,
)

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("productions.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active")
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    workspace_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    content_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_auto_saved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    statistics: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    public_facts: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    follow_up_questions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    rejection_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Production"] = relationship(back_populates="research_sessions")
    sources: Mapped[list["ResearchSource"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    notes: Mapped[list["ResearchNote"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    bookmarks: Mapped[list["ResearchBookmark"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    fact_checks: Mapped[list["ResearchFactCheck"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    comments: Mapped[list["ResearchComment"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    versions: Mapped[list["ResearchVersion"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    timeline_events: Mapped[list["ResearchTimelineEvent"]] = relationship(back_populates="research", cascade="all, delete-orphan")
    ai_interactions: Mapped[list["ResearchAIInteraction"]] = relationship(back_populates="research", cascade="all, delete-orphan")



class ResearchAIInteraction(Base):
    __tablename__ = "research_ai_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[dict] = mapped_column(JSONB, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), default="demo", nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="ai_interactions")



class ResearchSource(Base):
    __tablename__ = "research_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    source_type: Mapped[str] = mapped_column(String(64), default="article")
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="sources")



class ResearchNote(Base):
    __tablename__ = "research_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    research: Mapped[ResearchSession] = relationship(back_populates="notes")



class ResearchBookmark(Base):
    __tablename__ = "research_bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(32), default="gold")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="bookmarks")



class ResearchFactCheck(Base):
    __tablename__ = "research_fact_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    source_id: Mapped[int | None] = mapped_column(ForeignKey("research_sources.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    checked_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="fact_checks")



class ResearchComment(Base):
    __tablename__ = "research_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="comments")



class ResearchVersion(Base):
    __tablename__ = "research_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    workspace_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="versions")



class ResearchTimelineEvent(Base):
    __tablename__ = "research_timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    research_id: Mapped[int] = mapped_column(ForeignKey("research_sessions.id", ondelete="CASCADE"), index=True)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), default="milestone")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    research: Mapped[ResearchSession] = relationship(back_populates="timeline_events")
