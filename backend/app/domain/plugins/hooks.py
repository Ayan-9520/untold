"""Studio hook points — extension points plugins can register handlers for."""

from __future__ import annotations

HOOK_POINTS: dict[str, dict] = {
    "workflow.before_node": {
        "label": "Before Workflow Node",
        "description": "Runs before a workflow node executes. Can mutate context or skip node.",
        "category": "workflow",
        "input_schema": {"run_id": "int", "node_id": "string", "context": "object"},
        "output_schema": {"skip": "boolean?", "context": "object?"},
    },
    "workflow.after_node": {
        "label": "After Workflow Node",
        "description": "Runs after a workflow node completes. Can transform output.",
        "category": "workflow",
        "input_schema": {"run_id": "int", "node_id": "string", "output": "object"},
        "output_schema": {"output": "object?"},
    },
    "seo.format_title": {
        "label": "Format SEO Title",
        "description": "Transform SEO title before export or publish.",
        "category": "seo",
        "input_schema": {"title": "string", "project_id": "int"},
        "output_schema": {"title": "string"},
    },
    "seo.format_description": {
        "label": "Format SEO Description",
        "description": "Transform SEO description before export or publish.",
        "category": "seo",
        "input_schema": {"description": "string", "project_id": "int"},
        "output_schema": {"description": "string"},
    },
    "script.before_export": {
        "label": "Before Script Export",
        "description": "Transform script content before markdown/Word export.",
        "category": "production",
        "input_schema": {"script_id": "int", "content": "string"},
        "output_schema": {"content": "string"},
    },
    "dashboard.widgets": {
        "label": "Dashboard Widgets",
        "description": "Register custom dashboard widget definitions for the Studio home.",
        "category": "ui",
        "input_schema": {"user_id": "int"},
        "output_schema": {"widgets": "array"},
    },
    "nav.items": {
        "label": "Navigation Items",
        "description": "Inject sidebar navigation items (frontend only).",
        "category": "ui",
        "input_schema": {},
        "output_schema": {"items": "array"},
    },
}
