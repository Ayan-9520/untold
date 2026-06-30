"""Core Studio entities — Production pipeline root aggregate."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Production(Base):
    """Studio project — documentary production across the pipeline."""

    __tablename__ = "productions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(16), default="en", nullable=False)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    stage: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    publishing_status: Mapped[str] = mapped_column(String(32), default="unpublished", nullable=False)
    assignee: Mapped[str] = mapped_column(String(120), nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    sources_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    seo_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    seo_keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    visibility: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    video_id: Mapped[int | None] = mapped_column(ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    agent_jobs: Mapped[list["AIAgentJob"]] = relationship(back_populates="production", cascade="all, delete-orphan")
    members: Mapped[list["StudioProjectMember"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    research_sessions: Mapped[list["ResearchSession"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    scripts: Mapped[list["Script"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    storyboard_scenes: Mapped[list["StoryboardScene"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    storyboard_revisions: Mapped[list["StoryboardRevision"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    assets: Mapped[list["StudioAsset"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    ai_generations: Mapped[list["AIGeneration"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    voice_generations: Mapped[list["VoiceGeneration"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[list["StudioTask"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    approvals: Mapped[list["StudioApproval"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    publish_jobs: Mapped[list["PublishJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    comments: Mapped[list["ProjectComment"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    timeline_session: Mapped["TimelineSession | None"] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )
    timeline_export_jobs: Mapped[list["TimelineExportJob"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class AIAgentJob(Base):
    """Task queued for a Studio AI agent (Research, Script, Thumbnail, etc.)."""

    __tablename__ = "ai_agent_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    production_id: Mapped[int | None] = mapped_column(
        ForeignKey("productions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    production: Mapped[Production | None] = relationship(back_populates="agent_jobs")
