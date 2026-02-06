import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users(auth_client: AsyncClient):
    resp = await auth_client.get("/api/admin/users")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_user(auth_client: AsyncClient, seed):
    tenant_id = str(seed["system_tenant"].id)
    resp = await auth_client.post(
        "/api/admin/users",
        json={
            "email": "newuser@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_create_duplicate_email(auth_client: AsyncClient, seed):
    tenant_id = str(seed["system_tenant"].id)
    await auth_client.post(
        "/api/admin/users",
        json={
            "email": "dup@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    resp = await auth_client.post(
        "/api/admin/users",
        json={
            "email": "dup@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_user(auth_client: AsyncClient, seed):
    tenant_id = str(seed["system_tenant"].id)
    create_resp = await auth_client.post(
        "/api/admin/users",
        json={
            "email": "update@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    user_id = create_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/admin/users/{user_id}",
        json={"role_id": 2, "is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_deactivate_user(auth_client: AsyncClient, seed):
    tenant_id = str(seed["system_tenant"].id)
    create_resp = await auth_client.post(
        "/api/admin/users",
        json={
            "email": "deactivate@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    user_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/admin/users/{user_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_users_unauthenticated(client: AsyncClient, seed):
    resp = await client.get("/api/admin/users")
    assert resp.status_code == 403 or resp.status_code == 401


@pytest.mark.asyncio
async def test_user_lifecycle(auth_client: AsyncClient, seed):
    """Full lifecycle: create -> verify -> update -> verify updated_at -> delete -> verify gone."""
    tenant_id = str(seed["system_tenant"].id)

    # Create
    create_resp = await auth_client.post(
        "/api/admin/users",
        json={
            "email": "lifecycle@test.com",
            "password": "password123",
            "role_id": 3,
            "tenant_id": tenant_id,
        },
    )
    assert create_resp.status_code == 201
    user = create_resp.json()
    user_id = user["id"]
    assert user["email"] == "lifecycle@test.com"
    assert user["created_at"] is not None
    assert user["updated_at"] is None

    # Update
    update_resp = await auth_client.patch(
        f"/api/admin/users/{user_id}",
        json={"role_id": 2},
    )
    assert update_resp.status_code == 200
    updated_user = update_resp.json()
    assert updated_user["role"] == "admin"
    assert updated_user["updated_at"] is not None

    # Delete
    delete_resp = await auth_client.delete(f"/api/admin/users/{user_id}")
    assert delete_resp.status_code == 204

    # Verify deleted (not in list)
    list_resp = await auth_client.get("/api/admin/users")
    user_ids = [u["id"] for u in list_resp.json()["items"]]
    assert user_id not in user_ids
