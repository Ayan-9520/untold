"""UNTOLD Studio — agent marketplace models."""

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

class MarketplaceAgent(Base):
    __tablename__ = "marketplace_agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(16), default="🤖", nullable=False)
    category: Mapped[str] = mapped_column(String(32), default="production", nullable=False, index=True)
    studio_route: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="published", nullable=False)
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("marketplace_agent_versions.id", ondelete="SET NULL"), nullable=True
    )
    default_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    available_permissions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    versions: Mapped[list["MarketplaceAgentVersion"]] = relationship(
        back_populates="agent",
        foreign_keys="MarketplaceAgentVersion.agent_id",
        cascade="all, delete-orphan",
    )



class MarketplaceAgentVersion(Base):
    __tablename__ = "marketplace_agent_versions"
    __table_args__ = (UniqueConstraint("agent_id", "version", name="uq_marketplace_agent_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("marketplace_agents.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    default_config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    changelog: Mapped[str | None] = mapped_column(String(500), nullable=True)
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    agent: Mapped[MarketplaceAgent] = relationship(
        back_populates="versions",
        foreign_keys=[agent_id],
    )



class AgentInstallation(Base):
    __tablename__ = "agent_installations"
    __table_args__ = (UniqueConstraint("user_id", "agent_id", name="uq_agent_installation_user_agent"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    agent_id: Mapped[int] = mapped_column(ForeignKey("marketplace_agents.id", ondelete="CASCADE"), index=True)
    installed_version_id: Mapped[int] = mapped_column(
        ForeignKey("marketplace_agent_versions.id", ondelete="RESTRICT"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    granted_permissions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped[MarketplaceAgent] = relationship()
    installed_version: Mapped[MarketplaceAgentVersion] = relationship()
    history: Mapped[list["AgentInstallationHistory"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )



class AgentInstallationHistory(Base):
    __tablename__ = "agent_installation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int] = mapped_column(ForeignKey("agent_installations.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    from_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    performed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    installation: Mapped[AgentInstallation] = relationship(back_populates="history")


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int | None] = mapped_column(
        ForeignKey("agent_installations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    agent_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), nullable=True)
    run_id: Mapped[int | None] = mapped_column(nullable=True)
    generation_id: Mapped[int | None] = mapped_column(ForeignKey("ai_generations.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success", nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(default=0, nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


class AgentMemoryEntry(Base):
    __tablename__ = "agent_memory_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int] = mapped_column(ForeignKey("agent_installations.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), nullable=True)
    memory_key: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AgentSchedule(Base):
    __tablename__ = "agent_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int] = mapped_column(ForeignKey("agent_installations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_installation_id: Mapped[int | None] = mapped_column(
        ForeignKey("agent_installations.id", ondelete="SET NULL"), nullable=True
    )
    to_installation_id: Mapped[int | None] = mapped_column(
        ForeignKey("agent_installations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    from_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    to_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), default="task", nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
