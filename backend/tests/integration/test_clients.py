import pytest
from httpx import AsyncClient

CLIENT_PAYLOAD = {
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1234567890",
    "address": "123 Main St",
    "billing_address": "PO Box 100",
    "notes": "Key client",
}


async def _create_client(auth_client: AsyncClient, **overrides) -> dict:
    payload = {**CLIENT_PAYLOAD, **overrides}
    resp = await auth_client.post("/api/clients", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_client(auth_client: AsyncClient):
    data = await _create_client(auth_client)
    assert data["name"] == "Acme Corp"
    assert data["email"] == "contact@acme.com"
    assert data["phone"] == "+1234567890"
    assert data["address"] == "123 Main St"
    assert data["billing_address"] == "PO Box 100"
    assert data["notes"] == "Key client"
    assert data["is_active"] is True
    assert data["property_count"] == 0
    assert data["created_at"] is not None
    assert data["updated_at"] is None

    # Duplicate name should fail
    resp = await auth_client.post("/api/clients", json=CLIENT_PAYLOAD)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_clients(auth_client: AsyncClient):
    await _create_client(auth_client, name="List Client A")
    await _create_client(auth_client, name="List Client B")

    resp = await auth_client.get("/api/clients")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    names = [c["name"] for c in data["items"]]
    assert "List Client A" in names
    assert "List Client B" in names


@pytest.mark.asyncio
async def test_get_client(auth_client: AsyncClient):
    created = await _create_client(auth_client, name="Get Client")

    resp = await auth_client.get(f"/api/clients/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Client"

    # Non-existent ID
    resp = await auth_client.get("/api/clients/00000000-0000-0000-0000-000000000099")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_client(auth_client: AsyncClient):
    created = await _create_client(auth_client, name="Update Client")

    resp = await auth_client.patch(
        f"/api/clients/{created['id']}",
        json={"notes": "Updated notes", "is_active": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["notes"] == "Updated notes"
    assert data["is_active"] is False
    assert data["updated_at"] is not None

    # Rename to existing name should fail
    await _create_client(auth_client, name="Other Client")
    resp = await auth_client.patch(
        f"/api/clients/{created['id']}",
        json={"name": "Other Client"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_delete_client(auth_client: AsyncClient):
    created = await _create_client(auth_client, name="Delete Client")

    # Add a property so we can verify cascade
    prop_resp = await auth_client.post("/api/properties", json={
        "client_id": created["id"],
        "property_type": "house",
        "name": "Test House",
        "address": "1 Delete St",
    })
    assert prop_resp.status_code == 201
    prop_id = prop_resp.json()["id"]

    # Delete client
    resp = await auth_client.delete(f"/api/clients/{created['id']}")
    assert resp.status_code == 204

    # Client gone from list and GET
    assert (await auth_client.get(f"/api/clients/{created['id']}")).status_code == 404

    # Property also soft-deleted
    assert (await auth_client.get(f"/api/properties/{prop_id}")).status_code == 404
