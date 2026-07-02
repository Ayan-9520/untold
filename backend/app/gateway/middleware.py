"""Gateway usage logging middleware."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.db.session import SessionLocal
from app.services.api_gateway_service import ApiGatewayService

logger = logging.getLogger("untold.gateway")


class GatewayUsageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/gateway"):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)

        auth = getattr(request.state, "gateway_auth", None)
        if not auth:
            return response

        protocol = "graphql" if "/graphql" in request.url.path else "rest"
        environment = getattr(request.state, "gateway_environment", None)
        if not environment:
            environment = "sandbox" if "/gateway/sandbox" in request.url.path else "production"
        db = SessionLocal()
        try:
            ApiGatewayService.log_usage(
                db,
                auth=auth,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                protocol=protocol,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                environment=environment,
            )
        except Exception as exc:
            logger.warning("Failed to log gateway usage: %s", exc)
        finally:
            db.close()

        response.headers["X-Request-ID"] = auth.request_id or ""
        response.headers["X-API-Version"] = auth.api_version
        return response
