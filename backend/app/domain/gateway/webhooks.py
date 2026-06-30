"""Outbound webhook delivery for API Gateway consumers."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.studio_platform import ApiGatewayWebhook, ApiGatewayWebhookDelivery

logger = logging.getLogger("untold.gateway.webhooks")


def _sign_payload(secret: str, body: bytes) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def deliver_gateway_webhooks(db: Session, event_type: str, payload: dict, *, user_id: int | None = None) -> list[dict]:
    """Deliver event to all active webhooks subscribed to event_type."""
    q = db.query(ApiGatewayWebhook).filter(ApiGatewayWebhook.is_active.is_(True))
    if user_id is not None:
        q = q.filter(ApiGatewayWebhook.user_id == user_id)
    hooks = [h for h in q.all() if event_type in (h.events or [])]

    results = []
    envelope = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": payload,
    }
    body = json.dumps(envelope, default=str).encode()

    for hook in hooks:
        delivery = ApiGatewayWebhookDelivery(
            webhook_id=hook.id,
            event_type=event_type,
            payload=envelope,
            status="pending",
        )
        db.add(delivery)
        db.flush()

        signature = _sign_payload(hook.secret, body)
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    hook.url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-UNTOLD-Signature": signature,
                        "X-UNTOLD-Event": event_type,
                    },
                )
            delivery.attempts = 1
            delivery.http_status = resp.status_code
            delivery.response_body = (resp.text or "")[:2000]
            if 200 <= resp.status_code < 300:
                delivery.status = "delivered"
                delivery.delivered_at = datetime.now(timezone.utc)
                hook.last_triggered_at = datetime.now(timezone.utc)
                hook.failure_count = 0
            else:
                delivery.status = "failed"
                delivery.error_message = f"HTTP {resp.status_code}"
                hook.failure_count += 1
        except Exception as exc:
            delivery.attempts = 1
            delivery.status = "failed"
            delivery.error_message = str(exc)[:500]
            hook.failure_count += 1
            logger.warning("Gateway webhook %s delivery failed: %s", hook.id, exc)

        results.append({"webhook_id": hook.id, "delivery_id": delivery.id, "status": delivery.status})

    db.commit()
    return results
