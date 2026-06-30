"""Auth API integration tests."""

import uuid

import pytest


@pytest.mark.integration
def test_register_login_and_me(client):
    email = f"pytest-{uuid.uuid4().hex[:10]}@untold.test"
    password = "TestPass123!"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Pytest User"},
    )
    assert register.status_code == 201
    assert register.json()["email"] == email

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    tokens = login.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == email


@pytest.mark.integration
def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@untold.test", "password": "WrongPass123!"},
    )
    assert response.status_code == 401


@pytest.mark.integration
def test_studio_me_requires_studio_access(client, db_session):
    from tests.factories.user import create_user, user_token_headers

    user = create_user(db_session, email="no-studio@untold.test", studio_role=None)
    db_session.flush()
    headers = user_token_headers(user)

    response = client.get("/api/v1/auth/studio/me", headers=headers)
    assert response.status_code == 403


@pytest.mark.integration
def test_studio_me_for_studio_user(client, studio_auth_headers):
    response = client.get("/api/v1/auth/studio/me", headers=studio_auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["studio_role"]
    assert "permissions" in body


@pytest.mark.integration
def test_ai_prompt_rejects_script_tag(client, studio_auth_headers):
    response = client.post(
        "/api/v1/studio/platform/ai-studio/generate",
        headers=studio_auth_headers,
        json={"module": "script", "prompt": "<script>alert(1)</script>"},
    )
    assert response.status_code == 422
