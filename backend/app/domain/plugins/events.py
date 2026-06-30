"""Studio event catalog — events plugins can subscribe to."""

from __future__ import annotations

STUDIO_EVENTS: dict[str, dict] = {
    "workflow.run.started": {
        "label": "Workflow Run Started",
        "category": "workflow",
        "payload_schema": {"run_id": "int", "definition_id": "int", "project_id": "int|null"},
    },
    "workflow.run.finished": {
        "label": "Workflow Run Finished",
        "category": "workflow",
        "payload_schema": {"run_id": "int", "status": "string", "project_id": "int|null"},
    },
    "workflow.node.completed": {
        "label": "Workflow Node Completed",
        "category": "workflow",
        "payload_schema": {"run_id": "int", "node_id": "string", "output": "object"},
    },
    "publish.completed": {
        "label": "Publish Completed",
        "category": "publishing",
        "payload_schema": {"job_id": "int", "platform": "string", "project_id": "int"},
    },
    "publish.failed": {
        "label": "Publish Failed",
        "category": "publishing",
        "payload_schema": {"job_id": "int", "error": "string"},
    },
    "collab.comment.created": {
        "label": "Comment Created",
        "category": "collaboration",
        "payload_schema": {"comment_id": "int", "project_id": "int", "author_id": "int"},
    },
    "collab.task.created": {
        "label": "Task Created",
        "category": "collaboration",
        "payload_schema": {"task_id": "int", "project_id": "int"},
    },
    "collab.approval.requested": {
        "label": "Approval Requested",
        "category": "collaboration",
        "payload_schema": {"approval_id": "int", "project_id": "int"},
    },
    "script.saved": {
        "label": "Script Saved",
        "category": "production",
        "payload_schema": {"script_id": "int", "project_id": "int"},
    },
    "research.completed": {
        "label": "Research Completed",
        "category": "production",
        "payload_schema": {"research_id": "int", "project_id": "int"},
    },
    "ai.job.completed": {
        "label": "AI Job Completed",
        "category": "ai",
        "payload_schema": {"job_id": "int", "module": "string", "project_id": "int|null"},
    },
    "plugin.installed": {
        "label": "Plugin Installed",
        "category": "platform",
        "payload_schema": {"plugin_slug": "string", "installation_id": "int"},
    },
}
