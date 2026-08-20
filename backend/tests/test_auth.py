import uuid

from tests.conftest import SUPERADMIN_EMAIL, SUPERADMIN_PASSWORD


def _unique_email():
    return f"user-{uuid.uuid4().hex[:8]}@test.dev"


async def _register(client, email=None, **overrides):
    email = email or _unique_email()
    payload = {
        "email": email,
        "username": email.split("@")[0],
        "password": "password123",
        "role": "manager",
    }
    payload.update(overrides)
    return await client.post("/api/v1/auth/register", json=payload)


async def test_register_success(client):
    resp = await _register(client)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["is_active"] is False
    assert body["role"] == "manager"
    assert "id" in body


async def test_register_duplicate_email(client):
    email = _unique_email()
    first = await _register(client, email=email)
    assert first.status_code == 201
    second = await _register(client, email=email)
    assert second.status_code == 409


async def test_register_forbidden_role(client):
    resp = await _register(client, role="superadmin")
    assert resp.status_code == 400


async def test_register_invalid_role_422(client):
    resp = await _register(client, role="pirate")
    assert resp.status_code == 422


async def test_register_short_password(client):
    resp = await _register(client, password="short")
    assert resp.status_code == 422


async def test_register_invalid_email(client):
    resp = await _register(client, email="pas-un-email")
    assert resp.status_code == 422


async def test_login_superadmin(client):
    resp = await client.post(
        "/api/v1/auth/login/json",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_login_wrong_password(client):
    resp = await client.post(
        "/api/v1/auth/login/json",
        json={"email": SUPERADMIN_EMAIL, "password": "mauvais-mdp"},
    )
    assert resp.status_code == 401


async def test_login_inactive_user(client):
    email = _unique_email()
    await _register(client, email=email)
    resp = await client.post(
        "/api/v1/auth/login/json",
        json={"email": email, "password": "password123"},
    )
    assert resp.status_code == 403


async def test_me(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == SUPERADMIN_EMAIL


async def test_me_unauthorized(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_refresh_flow(client):
    login = await client.post(
        "/api/v1/auth/login/json",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
    )
    refresh_token = login.json()["refresh_token"]

    refreshed = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refreshed.status_code == 200, refreshed.text
    body = refreshed.json()
    assert body["access_token"]
    assert body["refresh_token"] != refresh_token

    old_again = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert old_again.status_code == 401


async def test_logout_revokes_refresh(client):
    login = await client.post(
        "/api/v1/auth/login/json",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
    )
    refresh_token = login.json()["refresh_token"]

    logout = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert logout.status_code == 204

    refreshed = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refreshed.status_code == 401


async def test_protected_route_without_token(client):
    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 401