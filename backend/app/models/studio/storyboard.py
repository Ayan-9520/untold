"""UNTOLD Studio — storyboard models."""

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

class StoryboardScene(Base):
    __tablename__ = "storyboard_scenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("productions.id", ondelete="CASCADE"), index=True)
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    narration: Mapped[str | None] = mapped_column(Text, nullable=True)
    camera_angle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    camera_movement: Mapped[str | None] = mapped_column(String(120), nullable=True)
    visual_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    environment: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lighting: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dialogue: Mapped[str | None] = mapped_column(Text, nullable=True)
    shot_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mood: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transition: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reference_image_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Production"] = relationship(back_populates="storyboard_scenes")



class StoryboardAIInteraction(Base):
    __tablename__ = "storyboard_ai_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("productions.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    response: Mapped[dict] = mapped_column(JSONB, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), default="demo", nullable=False)
    ai_generation_id: Mapped[int | None] = mapped_column(ForeignKey("ai_generations.id", ondelete="SET NULL"), nullable=True)
    scenes_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class StoryboardRevision(Base):
    __tablename__ = "storyboard_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("productions.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(300), nullable=True)
    scenes_snapshot: Mapped[dict | list] = mapped_column(JSONB, nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Production"] = relationship(back_populates="storyboard_revisions")
