"""UNTOLD Studio — AI models."""

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

class AIGeneration(Base):
    __tablename__ = "ai_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), index=True)
    module: Mapped[AIGenerationModule] = mapped_column(StrEnum(AIGenerationModule))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), default="demo", nullable=False)
    status: Mapped[AIGenerationStatus] = mapped_column(StrEnum(AIGenerationStatus), default=AIGenerationStatus.QUEUED)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[float | None] = mapped_column(nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(32), default="none", nullable=False)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    temperature: Mapped[float | None] = mapped_column(nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    parent_generation_id: Mapped[int | None] = mapped_column(ForeignKey("ai_generations.id", ondelete="SET NULL"), nullable=True, index=True)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Production | None"] = relationship(back_populates="ai_generations")



class AIPromptLibrary(Base):
    __tablename__ = "ai_prompt_library"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    prompt_key: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )



class AIImageCollection(Base):
    __tablename__ = "ai_image_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIImageCollectionItem(Base):
    __tablename__ = "ai_image_collection_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("ai_image_collections.id", ondelete="CASCADE"), index=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIImageVersion(Base):
    __tablename__ = "ai_image_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIVideoVersion(Base):
    __tablename__ = "ai_video_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIVoiceVersion(Base):
    __tablename__ = "ai_voice_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIMusicVersion(Base):
    __tablename__ = "ai_music_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIShortsVersion(Base):
    __tablename__ = "ai_shorts_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AISEOVariant(Base):
    __tablename__ = "ai_seo_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    variant: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    seo_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AITranslationVersion(Base):
    __tablename__ = "ai_translation_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("ai_generations.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    result_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    output_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AITranslationMemory(Base):
    __tablename__ = "ai_translation_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_lang: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    target_lang: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class VoiceGeneration(Base):
    __tablename__ = "voice_generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("productions.id", ondelete="CASCADE"), index=True)
    language: Mapped[str] = mapped_column(String(16), default="en")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    emotion: Mapped[str | None] = mapped_column(String(64), nullable=True)
    speed: Mapped[float] = mapped_column(Float, default=1.0)
    pitch: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[AIGenerationStatus] = mapped_column(StrEnum(AIGenerationStatus), default=AIGenerationStatus.QUEUED)
    audio_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    r2_key: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Production"] = relationship(back_populates="voice_generations")



class AICostBudget(Base):
    __tablename__ = "ai_cost_budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scope_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    scope_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    monthly_limit_usd: Mapped[float] = mapped_column(nullable=False)
    alert_threshold_pct: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    hard_limit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    alerts: Mapped[list["AICostAlert"]] = relationship(back_populates="budget", cascade="all, delete-orphan")



class AICostAlert(Base):
    __tablename__ = "ai_cost_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("ai_cost_budgets.id", ondelete="CASCADE"), index=True)
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False)
    threshold_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    spend_usd: Mapped[float] = mapped_column(nullable=False)
    limit_usd: Mapped[float] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    budget: Mapped[AICostBudget] = relationship(back_populates="alerts")



class AIModelPolicy(Base):
    __tablename__ = "ai_model_policies"
    __table_args__ = (UniqueConstraint("module", name="uq_ai_model_policy_module"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    selection_mode: Mapped[str] = mapped_column(String(32), default="auto", nullable=False)
    primary_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    primary_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fallback_chain: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    max_cost_per_request_usd: Mapped[float | None] = mapped_column(nullable=True)
    cache_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cache_ttl_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )



class AIResponseCache(Base):
    __tablename__ = "ai_response_cache"
    __table_args__ = (UniqueConstraint("cache_key", name="uq_ai_response_cache_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    response_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_saved_usd: Mapped[float] = mapped_column(default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())



class AIMonthlyCostReport(Base):
    __tablename__ = "ai_monthly_cost_reports"
    __table_args__ = (
        UniqueConstraint("year", "month", "scope_type", "scope_id", name="uq_ai_monthly_cost_report"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    scope_type: Mapped[str] = mapped_column(String(16), default="global", nullable=False)
    scope_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    report_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    generated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
