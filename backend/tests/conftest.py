"""Pytest configuration, fixtures, and environment bootstrap."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

# Configure environment before any `app` imports
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://untold:untold_secret@localhost:5432/untold_test",
)
os.environ.update(
    {
        "REDIS_URL": os.environ.get("REDIS_URL", "redis://localhost:6379/15"),
        "SECRET_KEY": "test-secret-key-minimum-32-characters-long",
        "ENVIRONMENT": "development",
        "SEED_DATABASE": "false",
        "RUN_MIGRATIONS": "true",
        "RATE_LIMIT_ENABLED": "false",
        "METRICS_ENABLED": "false",
        "OTEL_ENABLED": "false",
        "ENABLE_WEBSOCKET": "false",
    }
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def _reset_settings_cache() -> Generator[None, None, None]:
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def engine(_reset_settings_cache):
    from alembic import command
    from alembic.config import Config

    from app.core.config import get_settings

    cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")

    settings = get_settings()
    eng = create_engine(settings.database_url, poolclass=NullPool, pool_pre_ping=True)
    yield eng
    eng.dispose()


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session) -> Generator:
    from fastapi.testclient import TestClient

    from app.db.session import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(db_session):
    from tests.factories.user import create_user, user_token_headers

    user = create_user(db_session, email="auth-fixture@untold.test", password="TestPass123!")
    db_session.flush()
    return user_token_headers(user)


@pytest.fixture()
def studio_auth_headers(db_session):
    from tests.factories.user import create_studio_user, user_token_headers

    user = create_studio_user(db_session, email="studio-fixture@untold.test")
    db_session.flush()
    return user_token_headers(user)
