"""JWT security unit tests."""

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password, get_password_hash


@pytest.mark.unit
def test_password_hash_roundtrip():
    hashed = get_password_hash("StrongPass123!")
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.unit
def test_access_token_contains_issuer_and_type():
    token = create_access_token(42, {"is_admin": True})
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"
    assert payload["iss"] == get_settings().jwt_issuer
    assert payload["is_admin"] is True


@pytest.mark.unit
def test_refresh_token_type():
    token = create_refresh_token(7, session_id="sess-abc")
    payload = decode_token(token)
    assert payload["type"] == "refresh"
    assert payload["jti"] == "sess-abc"


@pytest.mark.unit
def test_decode_rejects_wrong_issuer():
    settings = get_settings()
    bad = jwt.encode(
        {"sub": "1", "type": "access", "iss": "evil"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    with pytest.raises(ValueError, match="issuer"):
        decode_token(bad)
