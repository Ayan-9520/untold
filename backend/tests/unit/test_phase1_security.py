"""Phase 1 critical security fixes — unit tests."""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.domain.storage.local import LocalStorageProvider
from app.services.live_provider_service import verify_live_webhook_signature
from app.services.payment_service import PaymentService


def _configure_production(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    monkeypatch.setenv("ENCRYPTION_KEY", "y" * 32)
    monkeypatch.setenv("CORS_ORIGINS", "https://untold.com")
    monkeypatch.setenv("TRUSTED_HOSTS", "untold.com,api.untold.com")
    monkeypatch.setenv("DATABASE_URL", "postgresql://untold:secret@db.internal:5432/untold_db")
    monkeypatch.setenv("REDIS_URL", "redis://redis.internal:6379/0")
    monkeypatch.setenv("CELERY_BROKER_URL", "redis://redis.internal:6379/1")
    monkeypatch.setenv("CELERY_RESULT_BACKEND", "redis://redis.internal:6379/2")
    monkeypatch.setenv("AI_DEFAULT_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDINGS_DEFAULT_PROVIDER", "openai")
    monkeypatch.setenv("VECTORSTORE_DEFAULT_PROVIDER", "pgvector")
    monkeypatch.setenv("IMAGE_DEFAULT_PROVIDER", "openai_images")
    monkeypatch.setenv("VIDEO_DEFAULT_PROVIDER", "runway")
    monkeypatch.setenv("VOICE_DEFAULT_PROVIDER", "elevenlabs")
    monkeypatch.setenv("AI_ALLOW_DEMO_IN_PRODUCTION", "false")
    get_settings.cache_clear()


@pytest.mark.unit
def test_local_storage_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setenv("UNTOLD_UPLOAD_DIR", str(tmp_path))
    provider = LocalStorageProvider()
    with pytest.raises(ForbiddenError):
        provider.resolve_path("../../etc/passwd")


@pytest.mark.unit
def test_local_storage_confines_resolved_path(tmp_path, monkeypatch):
    monkeypatch.setenv("UNTOLD_UPLOAD_DIR", str(tmp_path))
    provider = LocalStorageProvider()
    safe = provider.resolve_path("images/test.png")
    assert safe.resolve().is_relative_to(Path(tmp_path).resolve())


@pytest.mark.unit
def test_stripe_webhook_rejects_unsigned_payload_in_production(monkeypatch):
    _configure_production(monkeypatch)
    with pytest.raises(UnauthorizedError):
        PaymentService.handle_stripe_webhook(None, b"{}", None)
    get_settings.cache_clear()


@pytest.mark.unit
def test_live_webhook_requires_signature_in_production(monkeypatch):
    _configure_production(monkeypatch)
    with pytest.raises(UnauthorizedError):
        verify_live_webhook_signature(b"{}", None)
    get_settings.cache_clear()


@pytest.mark.unit
def test_live_webhook_validates_hmac(monkeypatch):
    monkeypatch.setenv("LIVE_WEBHOOK_SECRET", "test-secret")
    get_settings.cache_clear()
    payload = b'{"event":"goal"}'
    sig = hmac.new(b"test-secret", payload, hashlib.sha256).hexdigest()
    verify_live_webhook_signature(payload, sig)
    with pytest.raises(UnauthorizedError):
        verify_live_webhook_signature(payload, "bad-signature")
    get_settings.cache_clear()


@pytest.mark.unit
def test_capability_registry_skips_demo_in_production(monkeypatch):
    _configure_production(monkeypatch)
    monkeypatch.setenv("AI_ENABLED_PROVIDERS", "demo")
    get_settings.cache_clear()

    from app.ai.capability_registry import CapabilityRegistry
    from app.domain.ai.providers.demo import DemoProvider

    registry = CapabilityRegistry()
    registry.register("llm", DemoProvider())
    with pytest.raises(RuntimeError):
        registry.resolve("llm", "demo", module="research")
    get_settings.cache_clear()
