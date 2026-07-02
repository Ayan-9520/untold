"""API Gateway scopes and permission catalog."""

from __future__ import annotations

GATEWAY_SCOPES: dict[str, dict] = {
    "videos.read": {"label": "Read Videos", "description": "List and retrieve video catalog entries."},
    "videos.write": {"label": "Write Videos", "description": "Create and update videos."},
    "projects.read": {"label": "Read Projects", "description": "List and retrieve studio productions."},
    "projects.write": {"label": "Write Projects", "description": "Update production metadata."},
    "analytics.read": {"label": "Read Analytics", "description": "Access analytics summaries via the gateway."},
    "webhooks.manage": {"label": "Manage Webhooks", "description": "Register and manage outbound webhooks."},
    "graphql.query": {"label": "GraphQL Query", "description": "Execute GraphQL queries against the gateway."},
    "gateway.admin": {"label": "Gateway Admin", "description": "Full gateway management (internal)."},
}

DEFAULT_API_KEY_SCOPES = ["videos.read", "projects.read", "graphql.query"]

RATE_LIMIT_TIERS: dict[str, dict] = {
    "free": {"label": "Free", "limit": "60/minute", "burst": 10},
    "standard": {"label": "Standard", "limit": "300/minute", "burst": 50},
    "enterprise": {"label": "Enterprise", "limit": "2000/minute", "burst": 200},
}

DEVELOPER_ACCOUNT_TIERS: dict[str, dict] = {
    "free": {"label": "Free", "max_active_keys": 3, "allowed_rate_tiers": frozenset({"free"})},
    "standard": {"label": "Standard", "max_active_keys": 10, "allowed_rate_tiers": frozenset({"free", "standard"})},
    "enterprise": {"label": "Enterprise", "max_active_keys": 50, "allowed_rate_tiers": frozenset({"free", "standard", "enterprise"})},
}

SUPPORTED_VERSIONS = ("v1", "v2")
DEFAULT_VERSION = "v1"

WEBHOOK_EVENTS = (
    "video.created",
    "video.updated",
    "video.published",
    "project.created",
    "project.updated",
    "project.completed",
    "api_key.used",
)
