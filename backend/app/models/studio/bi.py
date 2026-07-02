"""Business Intelligence ORM models."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BIMetricSnapshot(Base):
    __tablename__ = "bi_metric_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "snapshot_date",
            "metric_namespace",
            "metric_key",
            name="uq_bi_metric_snapshot",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    metric_namespace: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_key: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    dimensions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BIReportDefinition(Base):
    __tablename__ = "bi_report_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True
    )
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_type: Mapped[str] = mapped_column(String(64), default="custom", nullable=False)
    metrics: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    filters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    dimensions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    chart_type: Mapped[str] = mapped_column(String(32), default="bar", nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    runs: Mapped[list["BIReportRun"]] = relationship(back_populates="report", cascade="all, delete-orphan")
    schedules: Mapped[list["BIScheduledReport"]] = relationship(
        back_populates="report", cascade="all, delete-orphan"
    )


class BIReportRun(Base):
    __tablename__ = "bi_report_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("bi_report_definitions.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped[BIReportDefinition] = relationship(back_populates="runs")


class BIScheduledReport(Base):
    __tablename__ = "bi_scheduled_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("bi_report_definitions.id", ondelete="CASCADE"))
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(120), nullable=False)
    export_format: Mapped[str] = mapped_column(String(16), default="csv", nullable=False)
    recipients: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped[BIReportDefinition] = relationship(back_populates="schedules")
