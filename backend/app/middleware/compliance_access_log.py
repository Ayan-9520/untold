"""Compliance access logging middleware — SOC2 / ISO27001 access monitoring."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings

logger = logging.getLogger("untold.compliance.access")

_SKIP_PREFIXES = ("/health", "/live", "/ready", "/metrics", "/docs", "/redoc", "/openapi.json")
_SKIP_EXACT = {"/"}


class ComplianceAccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        path = request.url.path
        if not settings.compliance_access_log_enabled:
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)
        if path in _SKIP_EXACT or any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        user_id = None
        user_email = None
        auth_method = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.lower().startswith("bearer "):
            auth_method = "jwt"
            try:
                from app.core.security import decode_token
                from app.db.session import SessionLocal
                from app.models import User

                payload = decode_token(auth_header[7:])
                if payload.get("type") == "access" and payload.get("sub"):
                    user_id = int(payload["sub"])
                    db = SessionLocal()
                    try:
                        user = db.query(User).filter(User.id == user_id).first()
                        user_email = user.email if user else None
                    finally:
                        db.close()
            except Exception:
                pass
        elif request.headers.get("X-API-Key"):
            auth_method = "api_key"

        if user_id is None and auth_method != "api_key":
            return response

        from app.db.session import SessionLocal
        from app.services.compliance_service import ComplianceService

        db = SessionLocal()
        try:
            forwarded = request.headers.get("X-Forwarded-For")
            ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)
            ComplianceService.log_access(
                db,
                user_id=user_id,
                user_email=user_email,
                method=request.method,
                path=path,
                status_code=response.status_code,
                ip_address=ip,
                user_agent=request.headers.get("user-agent"),
                auth_method=auth_method,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            logger.warning("Access log write failed: %s", exc)
        finally:
            db.close()

        return response
