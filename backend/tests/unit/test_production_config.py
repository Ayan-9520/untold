"""Production configuration guardrails."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def _prod_settings(**overrides):
    base = {
        "environment": "production",
        "debug": False,
        "secret_key": "a" * 32,
        "encryption_key": "b" * 32,
        "cors_origins": "https://untold.com",
        "trusted_hosts": "untold.com,api.untold.com",
        "database_url": "postgresql://user:pass@db.internal:5432/untold_db",
        "redis_url": "redis://redis.internal:6379/0",
        "celery_broker_url": "redis://redis.internal:6379/1",
        "celery_result_backend": "redis://redis.internal:6379/2",
        "ai_default_provider": "openai",
        "embeddings_default_provider": "openai",
        "vectorstore_default_provider": "pgvector",
        "image_default_provider": "openai_images",
        "video_default_provider": "runway",
        "voice_default_provider": "elevenlabs",
        "ai_allow_demo_in_production": False,
    }
    base.update(overrides)
    return Settings(**base)


@pytest.mark.unit
def test_production_rejects_localhost_database():
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        _prod_settings(database_url="postgresql://untold:secret@localhost:5432/untold_db")


@pytest.mark.unit
def test_production_rejects_wildcard_trusted_hosts():
    with pytest.raises(ValidationError, match="TRUSTED_HOSTS"):
        _prod_settings(trusted_hosts="*")


@pytest.mark.unit
def test_production_rejects_demo_ai_provider():
    with pytest.raises(ValidationError, match="demo"):
        _prod_settings(ai_default_provider="demo")


@pytest.mark.unit
def test_production_accepts_valid_config():
    settings = _prod_settings()
    assert settings.is_production
    assert settings.trusted_host_list == ["untold.com", "api.untold.com"]
