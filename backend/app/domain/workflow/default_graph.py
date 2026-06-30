"""Default workflow graphs — system templates for UNTOLD Studio."""

from __future__ import annotations

from app.domain.workflow.nodes import NODE_CATALOG

DOC_PIPELINE_TYPES: tuple[str, ...] = (
    "research",
    "script",
    "storyboard",
    "image",
    "video",
    "voice",
    "music",
    "seo",
    "translation",
    "approval",
    "publishing",
    "analytics",
)


def _label(node_type: str) -> str:
    for item in NODE_CATALOG:
        if item["type"] == node_type:
            return item["label"]
    return node_type.title()


def documentary_pipeline_graph(*, x_spacing: int = 220, y: float = 120) -> dict:
    """Linear documentary production pipeline — matches studio ecosystem flow."""
    nodes: list[dict] = []
    edges: list[dict] = []
    for i, node_type in enumerate(DOC_PIPELINE_TYPES):
        node_id = f"n_{node_type}"
        catalog = next((c for c in NODE_CATALOG if c["type"] == node_type), {})
        nodes.append(
            {
                "id": node_id,
                "type": node_type,
                "position": {"x": i * x_spacing, "y": y},
                "data": {
                    "label": _label(node_type),
                    "retries": catalog.get("default_retries", 2),
                    "timeout_seconds": catalog.get("default_timeout"),
                },
            }
        )
        if i > 0:
            prev_id = f"n_{DOC_PIPELINE_TYPES[i - 1]}"
            edges.append(
                {
                    "id": f"e_{DOC_PIPELINE_TYPES[i - 1]}_{node_type}",
                    "source": prev_id,
                    "target": node_id,
                    "sourceHandle": "default",
                    "targetHandle": "in",
                }
            )
    return {
        "nodes": nodes,
        "edges": edges,
        "viewport": {"x": 0, "y": 0, "zoom": 0.85},
    }


SYSTEM_TEMPLATES: list[dict] = [
    {
        "name": "Documentary Production Pipeline",
        "description": "Research → Script → Storyboard → Image → Video → Voice → Music → SEO → Translation → Approval → Publishing → Analytics",
        "is_system": True,
        "graph": documentary_pipeline_graph(),
    },
]
