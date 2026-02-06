import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "admin@system.com", "password": "admin123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "admin@system.com", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient, seed):
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "admin123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client: AsyncClient):
    resp = await auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "admin@system.com"
    assert data["role"] == "superadmin"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient, seed):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403 or resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, seed):
    login_resp = await client.post(
        "/api/auth/login",
        json={"email": "admin@system.com", "password": "admin123"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
