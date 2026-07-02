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

SHORTS_PIPELINE_TYPES: tuple[str, ...] = (
    "research",
    "script",
    "parallel",
    "seo",
    "approval",
    "publishing",
)


def _label(node_type: str) -> str:
    for item in NODE_CATALOG:
        if item["type"] == node_type:
            return item["label"]
    return node_type.title()


def _linear_graph(types: tuple[str, ...], *, x_spacing: int = 220, y: float = 120) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []
    for i, node_type in enumerate(types):
        node_id = f"n_{node_type}_{i}"
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
            prev_id = f"n_{types[i - 1]}_{i - 1}"
            edges.append(
                {
                    "id": f"e_{i}",
                    "source": prev_id,
                    "target": node_id,
                    "sourceHandle": "default",
                    "targetHandle": "in",
                }
            )
    return {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.85}}


def documentary_pipeline_graph(*, x_spacing: int = 220, y: float = 120) -> dict:
    """Linear documentary production pipeline."""
    types = DOC_PIPELINE_TYPES
    nodes: list[dict] = []
    edges: list[dict] = []
    for i, node_type in enumerate(types):
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
            prev_id = f"n_{types[i - 1]}"
            edges.append(
                {
                    "id": f"e_{types[i - 1]}_{node_type}",
                    "source": prev_id,
                    "target": node_id,
                    "sourceHandle": "default",
                    "targetHandle": "in",
                }
            )
    return {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.85}}


def shorts_fast_publish_graph() -> dict:
    """Research → Script → Parallel (image+voice) → SEO → Approval → Publish."""
    return {
        "nodes": [
            {"id": "n_research", "type": "research", "position": {"x": 0, "y": 120}, "data": {"label": "Research"}},
            {"id": "n_script", "type": "script", "position": {"x": 220, "y": 120}, "data": {"label": "Script"}},
            {"id": "n_parallel", "type": "parallel", "position": {"x": 440, "y": 120}, "data": {"label": "Parallel assets"}},
            {"id": "n_image", "type": "image", "position": {"x": 620, "y": 40}, "data": {"label": "Thumbnail"}},
            {"id": "n_voice", "type": "voice", "position": {"x": 620, "y": 200}, "data": {"label": "Voice-over"}},
            {"id": "n_seo", "type": "seo", "position": {"x": 860, "y": 120}, "data": {"label": "SEO Pack"}},
            {"id": "n_approval", "type": "approval", "position": {"x": 1080, "y": 120}, "data": {"label": "Approval"}},
            {"id": "n_publish", "type": "publishing", "position": {"x": 1300, "y": 120}, "data": {"label": "Publishing"}},
            {"id": "n_notify", "type": "notification", "position": {"x": 1520, "y": 120}, "data": {"label": "Notify team", "title": "Shorts ready"}},
        ],
        "edges": [
            {"id": "e1", "source": "n_research", "target": "n_script"},
            {"id": "e2", "source": "n_script", "target": "n_parallel"},
            {"id": "e3", "source": "n_parallel", "target": "n_image"},
            {"id": "e4", "source": "n_parallel", "target": "n_voice"},
            {"id": "e5", "source": "n_image", "target": "n_seo"},
            {"id": "e6", "source": "n_voice", "target": "n_seo"},
            {"id": "e7", "source": "n_seo", "target": "n_approval"},
            {"id": "e8", "source": "n_approval", "target": "n_publish"},
            {"id": "e9", "source": "n_publish", "target": "n_notify"},
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 0.75},
    }


def translation_review_graph() -> dict:
    """Script → Translation → Condition → Approval loop."""
    return {
        "nodes": [
            {"id": "n_script", "type": "script", "position": {"x": 0, "y": 100}, "data": {"label": "Source script"}},
            {"id": "n_translate", "type": "translation", "position": {"x": 240, "y": 100}, "data": {"label": "Translate"}},
            {"id": "n_cond", "type": "condition", "position": {"x": 480, "y": 100}, "data": {"label": "Has translation?", "expression": "translation"}},
            {"id": "n_approval", "type": "approval", "position": {"x": 720, "y": 100}, "data": {"label": "Review"}},
            {"id": "n_notify", "type": "notification", "position": {"x": 960, "y": 100}, "data": {"label": "Notify", "title": "Translation approved"}},
        ],
        "edges": [
            {"id": "e1", "source": "n_script", "target": "n_translate"},
            {"id": "e2", "source": "n_translate", "target": "n_cond"},
            {"id": "e3", "source": "n_cond", "target": "n_approval", "sourceHandle": "true"},
            {"id": "e4", "source": "n_approval", "target": "n_notify"},
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 0.9},
    }


SYSTEM_TEMPLATES: list[dict] = [
    {
        "name": "Documentary Production Pipeline",
        "description": "Research → Script → Storyboard → Image → Video → Voice → Music → SEO → Translation → Approval → Publishing → Analytics",
        "is_system": True,
        "graph": documentary_pipeline_graph(),
    },
    {
        "name": "Shorts Fast Publish",
        "description": "Parallel image + voice assets with approval gate and team notification",
        "is_system": True,
        "graph": shorts_fast_publish_graph(),
    },
    {
        "name": "Translation Review",
        "description": "Script translation with condition gate and approval notification",
        "is_system": True,
        "graph": translation_review_graph(),
    },
]
