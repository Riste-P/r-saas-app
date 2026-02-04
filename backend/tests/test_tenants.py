import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tenants(auth_client: AsyncClient):
    resp = await auth_client.get("/api/admin/tenants")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_create_tenant(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/api/admin/tenants",
        json={"name": "Acme Corp", "slug": "acme"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"
    assert data["slug"] == "acme"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_duplicate_slug(auth_client: AsyncClient):
    await auth_client.post(
        "/api/admin/tenants",
        json={"name": "First", "slug": "dup-slug"},
    )
    resp = await auth_client.post(
        "/api/admin/tenants",
        json={"name": "Second", "slug": "dup-slug"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_tenant(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/admin/tenants",
        json={"name": "Original", "slug": "original"},
    )
    tenant_id = create_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/admin/tenants/{tenant_id}",
        json={"name": "Updated", "is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_cannot_modify_system_tenant(auth_client: AsyncClient):
    # Get the system tenant id
    list_resp = await auth_client.get("/api/admin/tenants")
    system = next(t for t in list_resp.json()["items"] if t["slug"] == "system")

    resp = await auth_client.patch(
        f"/api/admin/tenants/{system['id']}",
        json={"name": "Hacked"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_deactivate_tenant(auth_client: AsyncClient):
    create_resp = await auth_client.post(
        "/api/admin/tenants",
        json={"name": "ToDeactivate", "slug": "deact"},
    )
    tenant_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/admin/tenants/{tenant_id}")
    assert resp.status_code == 204
