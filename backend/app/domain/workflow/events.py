"""Workflow realtime events — push to Studio WebSocket clients."""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger("untold.workflow.events")


def notify_workflow_event(user_id: int | None, *, run_id: int, event: str, payload: dict | None = None) -> None:
    """Fire-and-forget workflow event to connected Studio admin clients."""
    if not user_id:
        return
    message = {
        "type": "workflow_event",
        "event": event,
        "run_id": run_id,
        **(payload or {}),
    }
    try:
        from app.websocket.studio import manager

        asyncio.run(manager.send_to_user(user_id, message))
    except Exception:
        logger.debug("Workflow WS notify failed for user %s run %s", user_id, run_id, exc_info=True)
