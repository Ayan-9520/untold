"""Webhook delivery for publishing agent."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.studio_platform import PublishWebhook

logger = logging.getLogger("untold.publishing.webhooks")


def deliver_webhooks(
    db: Session,
    event: str,
    payload: dict,
    *,
    project_id: int | None = None,
) -> list[dict]:
    q = db.query(PublishWebhook).filter(PublishWebhook.is_active.is_(True))
    if project_id:
        q = q.filter((PublishWebhook.project_id == project_id) | (PublishWebhook.project_id.is_(None)))
    hooks = q.all()

    results: list[dict] = []
    body = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": payload,
    }
    raw = json.dumps(body, default=str)

    for hook in hooks:
        events = hook.events or []
        if event not in events and "*" not in events:
            continue
        headers = {"Content-Type": "application/json", "X-Untold-Event": event}
        if hook.secret:
            sig = hmac.new(hook.secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
            headers["X-Untold-Signature"] = f"sha256={sig}"
        status_code = None
        error = None
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(hook.url, content=raw, headers=headers)
                status_code = resp.status_code
                if resp.status_code >= 400:
                    error = f"HTTP {resp.status_code}"
        except Exception as exc:
            error = str(exc)
            logger.warning("Webhook %s failed: %s", hook.id, exc)

        hook.last_triggered_at = datetime.now(timezone.utc)
        results.append({
            "webhook_id": hook.id,
            "name": hook.name,
            "status_code": status_code,
            "error": error,
            "delivered": error is None,
        })

    if results:
        db.commit()
    return results
