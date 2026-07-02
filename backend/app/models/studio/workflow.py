"""UNTOLD Studio — workflow models."""

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

class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), index=True, nullable=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    current_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("workflow_definition_versions.id", ondelete="SET NULL"), nullable=True
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    versions: Mapped[list["WorkflowDefinitionVersion"]] = relationship(
        back_populates="definition",
        foreign_keys="WorkflowDefinitionVersion.definition_id",
        cascade="all, delete-orphan",
    )
    triggers: Mapped[list["WorkflowTrigger"]] = relationship(back_populates="definition", cascade="all, delete-orphan")



class WorkflowDefinitionVersion(Base):
    __tablename__ = "workflow_definition_versions"
    __table_args__ = (UniqueConstraint("definition_id", "version", name="uq_workflow_definition_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    definition_id: Mapped[int] = mapped_column(ForeignKey("workflow_definitions.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    graph: Mapped[dict] = mapped_column(JSONB, nullable=False)
    changelog: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    definition: Mapped[WorkflowDefinition] = relationship(
        back_populates="versions",
        foreign_keys=[definition_id],
    )



class WorkflowTrigger(Base):
    __tablename__ = "workflow_triggers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    definition_id: Mapped[int] = mapped_column(ForeignKey("workflow_definitions.id", ondelete="CASCADE"), index=True)
    version_id: Mapped[int | None] = mapped_column(
        ForeignKey("workflow_definition_versions.id", ondelete="SET NULL"), nullable=True
    )
    trigger_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    webhook_secret: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    api_key_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    api_key_prefix: Mapped[str | None] = mapped_column(String(12), nullable=True)
    email_token: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    cron_expression: Mapped[str | None] = mapped_column(String(120), nullable=True)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    definition: Mapped[WorkflowDefinition] = relationship(back_populates="triggers")


class WorkflowRunLog(Base):
    """Durable workflow execution log entries."""

    __tablename__ = "workflow_run_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("production_pipeline_runs.id", ondelete="CASCADE"), index=True)
    node_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    level: Mapped[str] = mapped_column(String(16), default="info", nullable=False)
    stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
