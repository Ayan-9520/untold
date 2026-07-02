"""Business Intelligence API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BIReportCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    report_type: str = "custom"
    metrics: list[str] = Field(default_factory=list)
    filters: dict[str, Any] = Field(default_factory=dict)
    dimensions: list[str] = Field(default_factory=list)
    chart_type: str = "bar"


class BIScheduleCreate(BaseModel):
    report_id: int
    name: str = Field(min_length=1, max_length=200)
    cron_expression: str = Field(min_length=5, max_length=120)
    export_format: str = "csv"
    recipients: list[str] = Field(default_factory=list)
