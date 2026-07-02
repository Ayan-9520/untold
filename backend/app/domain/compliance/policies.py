"""Default compliance policies — GDPR / SOC2 / ISO27001 aligned."""

from __future__ import annotations

DEFAULT_COMPLIANCE_POLICIES: list[dict] = [
    {
        "policy_key": "audit_logs",
        "name": "Audit & Security Logs",
        "description": "Tamper-evident security and compliance audit events.",
        "data_category": "audit",
        "retention_days": 2555,  # ~7 years SOC2
        "legal_basis": "legal_obligation",
        "frameworks": ["SOC2", "ISO27001", "GDPR"],
        "auto_purge": False,
    },
    {
        "policy_key": "access_logs",
        "name": "API Access Logs",
        "description": "Authenticated API access for access monitoring.",
        "data_category": "access",
        "retention_days": 365,
        "legal_basis": "legitimate_interest",
        "frameworks": ["SOC2", "ISO27001"],
        "auto_purge": True,
    },
    {
        "policy_key": "user_profile",
        "name": "User Profile Data",
        "description": "Account profile, preferences, and membership data.",
        "data_category": "pii",
        "retention_days": 365,
        "legal_basis": "contract",
        "frameworks": ["GDPR"],
        "auto_purge": False,
    },
    {
        "policy_key": "analytics_events",
        "name": "Product Analytics",
        "description": "Usage analytics and product telemetry.",
        "data_category": "analytics",
        "retention_days": 90,
        "legal_basis": "consent",
        "frameworks": ["GDPR"],
        "auto_purge": True,
    },
    {
        "policy_key": "marketing_consent",
        "name": "Marketing Communications",
        "description": "Email marketing and promotional outreach data.",
        "data_category": "marketing",
        "retention_days": 730,
        "legal_basis": "consent",
        "frameworks": ["GDPR"],
        "auto_purge": True,
    },
    {
        "policy_key": "privacy_requests",
        "name": "Privacy Request Records",
        "description": "DSAR and erasure request audit trail.",
        "data_category": "privacy",
        "retention_days": 1825,  # 5 years
        "legal_basis": "legal_obligation",
        "frameworks": ["GDPR", "SOC2"],
        "auto_purge": False,
    },
]

CONSENT_TYPES = ("essential", "analytics", "marketing", "third_party")
PRIVACY_REQUEST_TYPES = ("access", "erasure", "portability", "rectification", "restriction")
PRIVACY_REQUEST_STATUSES = ("pending", "in_progress", "completed", "rejected", "cancelled")
