"""Mobile API schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MobileDeviceRegister(BaseModel):
    app_type: str = Field(pattern="^(studio|originals)$")
    platform: str = Field(pattern="^(ios|android)$")
    device_token: str = Field(min_length=8, max_length=512)
    device_name: str | None = None
    push_enabled: bool = True
    meta: dict[str, Any] = Field(default_factory=dict)


class ApprovalAction(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    notes: str | None = None
