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
