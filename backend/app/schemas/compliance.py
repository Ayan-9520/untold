"""Enterprise compliance API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CompliancePolicyResponse(BaseModel):
    id: int
    policy_key: str
    name: str
    description: str | None
    data_category: str
    retention_days: int
    legal_basis: str
    frameworks: list[str]
    auto_purge: bool
    enabled: bool
    updated_at: datetime | None


class CompliancePolicyUpdate(BaseModel):
    retention_days: int | None = Field(None, ge=1, le=3650)
    auto_purge: bool | None = None
    enabled: bool | None = None
    description: str | None = None


class ConsentRecordRequest(BaseModel):
    consent_type: str
    granted: bool
    policy_version: str | None = None
    subject_email: EmailStr | None = None


class ConsentRecordResponse(BaseModel):
    id: int
    user_id: int | None
    subject_email: str | None
    consent_type: str
    granted: bool
    policy_version: str
    source: str
    recorded_at: datetime | None


class PrivacyRequestCreate(BaseModel):
    subject_email: EmailStr
    request_type: str
    details: str | None = None


class PrivacyRequestUpdate(BaseModel):
    status: str | None = None
    response_notes: str | None = None
    assigned_to_id: int | None = None


class PrivacyRequestResponse(BaseModel):
    id: int
    user_id: int | None
    subject_email: str
    request_type: str
    status: str
    details: str | None
    response_notes: str | None
    due_at: datetime | None
    completed_at: datetime | None
    created_at: datetime | None


class AccessLogResponse(BaseModel):
    id: int
    user_email: str | None
    method: str
    path: str
    status_code: int
    ip_address: str | None
    auth_method: str | None
    latency_ms: int | None
    created_at: datetime | None


class FullComplianceReportResponse(BaseModel):
    score: int
    status: str
    frameworks: list[str]
    framework_coverage: dict
    controls: list[dict]
    recommendations: list[str]
    metrics: dict
    generated_at: str
