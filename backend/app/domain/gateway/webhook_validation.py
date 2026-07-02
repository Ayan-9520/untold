"""Webhook endpoint validation for the developer platform."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from app.core.config import get_settings
from app.core.exceptions import BadRequestError


def validate_webhook_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        raise BadRequestError("Webhook URL must use http or https")
    if not parsed.netloc:
        raise BadRequestError("Webhook URL must include a host")
    settings = get_settings()
    if settings.is_production and parsed.scheme != "https":
        raise BadRequestError("Production webhooks must use HTTPS URLs")

    host = parsed.hostname or ""
    if host in ("localhost", "127.0.0.1", "::1"):
        if settings.is_production:
            raise BadRequestError("Webhook URL cannot target localhost in production")
        return url

    try:
        addr = ipaddress.ip_address(host)
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            raise BadRequestError("Webhook URL cannot target private or reserved addresses")
    except ValueError:
        pass

    return url
