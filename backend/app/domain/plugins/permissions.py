"""Plugin permission catalog — scoped capabilities for third-party extensions."""

from __future__ import annotations

PLUGIN_PERMISSIONS: dict[str, dict] = {
    "webhook.send": {
        "label": "Send Webhooks",
        "description": "POST outbound webhooks to configured URLs on plugin events.",
        "risk": "medium",
    },
    "notification.send": {
        "label": "Send Notifications",
        "description": "Create in-app Studio notifications for team members.",
        "risk": "low",
    },
    "ai.generate": {
        "label": "AI Generation",
        "description": "Invoke AI Studio generation endpoints on behalf of the user.",
        "risk": "high",
    },
    "workflow.read": {
        "label": "Read Workflows",
        "description": "Read workflow definitions, runs, and execution logs.",
        "risk": "low",
    },
    "workflow.write": {
        "label": "Modify Workflows",
        "description": "Create or update workflow definitions and triggers.",
        "risk": "high",
    },
    "project.read": {
        "label": "Read Projects",
        "description": "Read project metadata, scripts, and research content.",
        "risk": "low",
    },
    "project.write": {
        "label": "Write Projects",
        "description": "Modify project content, scripts, and assets.",
        "risk": "high",
    },
    "publish.schedule": {
        "label": "Schedule Publishing",
        "description": "Schedule or trigger publishing jobs.",
        "risk": "medium",
    },
    "collab.read": {
        "label": "Read Collaboration",
        "description": "Read comments, tasks, and shared files.",
        "risk": "low",
    },
    "collab.write": {
        "label": "Write Collaboration",
        "description": "Post comments, tasks, and shared files.",
        "risk": "medium",
    },
    "storage.read": {
        "label": "Read Storage",
        "description": "Read asset library files and metadata.",
        "risk": "low",
    },
    "admin.read": {
        "label": "Read Admin",
        "description": "Read admin analytics and audit logs.",
        "risk": "medium",
    },
}

DEFAULT_GRANTED_PERMISSIONS = ["notification.send", "webhook.send", "project.read", "workflow.read", "collab.read"]


def validate_permissions(requested: list[str], available: list[str]) -> list[str]:
    allowed = set(available)
    return [p for p in requested if p in allowed and p in PLUGIN_PERMISSIONS]
