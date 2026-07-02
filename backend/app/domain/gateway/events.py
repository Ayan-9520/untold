"""Gateway webhook event emission — fire-and-forget after domain mutations."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.domain.gateway.webhooks import deliver_gateway_webhooks

logger = logging.getLogger("untold.gateway.events")


def emit_gateway_event(
    event_type: str,
    payload: dict,
    *,
    user_id: int | None = None,
    db: Session | None = None,
) -> None:
    """Deliver a gateway webhook event without failing the caller's transaction."""
    own_session = db is None
    session = db or SessionLocal()
    try:
        deliver_gateway_webhooks(session, event_type, payload, user_id=user_id)
    except Exception as exc:
        logger.warning("Gateway event %s delivery failed: %s", event_type, exc)
        if own_session:
            session.rollback()
    finally:
        if own_session:
            session.close()
