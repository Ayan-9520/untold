"""UNTOLD Studio — plugins models."""

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

class PluginDefinition(Base):
    __tablename__ = "plugin_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(16), default="🧩", nullable=False)
    category: Mapped[str] = mapped_column(String(32), default="integration", nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(120), default="UNTOLD", nullable=False)
    author_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="published", nullable=False)
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("plugin_versions.id", ondelete="SET NULL"), nullable=True
    )
    manifest: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    default_settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    available_permissions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    backend_entry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    frontend_entry: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    versions: Mapped[list["PluginVersion"]] = relationship(
        back_populates="plugin",
        foreign_keys="PluginVersion.plugin_id",
        cascade="all, delete-orphan",
    )



class PluginVersion(Base):
    __tablename__ = "plugin_versions"
    __table_args__ = (UniqueConstraint("plugin_id", "version", name="uq_plugin_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("plugin_definitions.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    manifest: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    settings_schema: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    default_settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    changelog: Mapped[str | None] = mapped_column(String(500), nullable=True)
    release_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    plugin: Mapped[PluginDefinition] = relationship(
        back_populates="versions",
        foreign_keys=[plugin_id],
    )



class PluginInstallation(Base):
    __tablename__ = "plugin_installations"
    __table_args__ = (UniqueConstraint("user_id", "plugin_id", name="uq_plugin_installation_user_plugin"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    plugin_id: Mapped[int] = mapped_column(ForeignKey("plugin_definitions.id", ondelete="CASCADE"), index=True)
    installed_version_id: Mapped[int] = mapped_column(
        ForeignKey("plugin_versions.id", ondelete="RESTRICT"), nullable=False
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    granted_permissions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    installed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_enabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    plugin: Mapped[PluginDefinition] = relationship()
    installed_version: Mapped[PluginVersion] = relationship()
    history: Mapped[list["PluginInstallationHistory"]] = relationship(
        back_populates="installation", cascade="all, delete-orphan"
    )



class PluginInstallationHistory(Base):
    __tablename__ = "plugin_installation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int] = mapped_column(ForeignKey("plugin_installations.id", ondelete="CASCADE"), index=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    from_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    to_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    settings_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    performed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    installation: Mapped[PluginInstallation] = relationship(back_populates="history")



class PluginEventLog(Base):
    __tablename__ = "plugin_event_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    installation_id: Mapped[int | None] = mapped_column(
        ForeignKey("plugin_installations.id", ondelete="SET NULL"), nullable=True
    )
    plugin_slug: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    hook_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success", nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
