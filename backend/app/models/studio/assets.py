"""UNTOLD Studio — assets models."""

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

class StudioAsset(Base):
    __tablename__ = "studio_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), index=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    asset_type: Mapped[AssetType] = mapped_column(StrEnum(AssetType), default=AssetType.IMAGE)
    folder: Mapped[str] = mapped_column(String(32), default="images", index=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    r2_key: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, default=list)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    cloud_provider: Mapped[str] = mapped_column(String(32), default="local")
    collection_id: Mapped[int | None] = mapped_column(ForeignKey("asset_collections.id", ondelete="SET NULL"), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    uploaded_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["Production | None"] = relationship(back_populates="assets")
    collection: Mapped["AssetCollection | None"] = relationship(back_populates="assets")
    versions: Mapped[list["AssetVersion"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    permissions: Mapped[list["AssetPermission"]] = relationship(back_populates="asset", cascade="all, delete-orphan")



class AssetCollection(Base):
    __tablename__ = "asset_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("productions.id", ondelete="SET NULL"), index=True)
    color: Mapped[str] = mapped_column(String(32), default="gold")
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assets: Mapped[list[StudioAsset]] = relationship(back_populates="collection")



class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("studio_assets.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    r2_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped[StudioAsset] = relationship(back_populates="versions")



class AssetPermission(Base):
    __tablename__ = "asset_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("studio_assets.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    permission: Mapped[str] = mapped_column(String(32), default="read")
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    asset: Mapped[StudioAsset] = relationship(back_populates="permissions")
