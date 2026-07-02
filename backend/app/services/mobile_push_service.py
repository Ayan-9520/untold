"""Mobile push notification delivery (FCM/APNs ready)."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.studio.mobile import MobileDevice, MobilePushLog

logger = logging.getLogger(__name__)


class MobilePushService:
    @staticmethod
    def notify_user(
        db: Session,
        user_id: int | None,
        *,
        title: str,
        body: str | None = None,
        payload: dict | None = None,
        app_type: str | None = None,
    ) -> int:
        if not user_id:
            return 0
        q = db.query(MobileDevice).filter(
            MobileDevice.user_id == user_id,
            MobileDevice.push_enabled.is_(True),
        )
        if app_type:
            q = q.filter(MobileDevice.app_type == app_type)
        devices = q.all()
        sent = 0
        for device in devices:
            log = MobilePushLog(
                device_id=device.id,
                user_id=user_id,
                title=title,
                body=body,
                payload=payload or {},
                status="sent",
            )
            db.add(log)
            MobilePushService._dispatch(device, title, body, payload or {})
            sent += 1
        db.commit()
        return sent

    @staticmethod
    def _dispatch(device: MobileDevice, title: str, body: str | None, payload: dict) -> None:
        """Production hook — wire FCM/APNs credentials via env when available."""
        logger.info(
            "Mobile push dispatch platform=%s app=%s title=%s token=%s…",
            device.platform,
            device.app_type,
            title[:80],
            device.device_token[:16],
        )
