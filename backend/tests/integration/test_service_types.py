import pytest
from httpx import AsyncClient

SERVICE_TYPE_PAYLOAD = {
    "name": "Regular Cleaning",
    "description": "Standard cleaning service",
    "base_price": 50.00,
    "estimated_duration_minutes": 120,
    "checklist_items": [
        {"name": "Vacuum floors", "sort_order": 1},
        {"name": "Clean bathroom", "description": "Scrub toilet, sink, shower", "sort_order": 2},
    ],
}


async def _create_service_type(auth_client: AsyncClient, **overrides) -> dict:
    payload = {**SERVICE_TYPE_PAYLOAD, **overrides}
    resp = await auth_client.post("/api/service-types", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_service_type(auth_client: AsyncClient):
    data = await _create_service_type(auth_client)
    assert data["name"] == "Regular Cleaning"
    assert data["base_price"] == "50.0"
    assert data["estimated_duration_minutes"] == 120
    assert data["is_active"] is True
    assert len(data["checklist_items"]) == 2
    assert data["checklist_items"][0]["name"] == "Vacuum floors"
    assert data["checklist_items"][1]["description"] == "Scrub toilet, sink, shower"
    assert data["created_at"] is not None
    assert data["updated_at"] is None

    # Duplicate name should fail
    resp = await auth_client.post("/api/service-types", json=SERVICE_TYPE_PAYLOAD)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_service_types(auth_client: AsyncClient):
    await _create_service_type(auth_client, name="List Test 1")
    await _create_service_type(auth_client, name="List Test 2")

    resp = await auth_client.get("/api/service-types")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 2
    names = [st["name"] for st in data["items"]]
    assert "List Test 1" in names
    assert "List Test 2" in names


@pytest.mark.asyncio
async def test_get_service_type(auth_client: AsyncClient):
    created = await _create_service_type(auth_client, name="Get Test")

    resp = await auth_client.get(f"/api/service-types/{created['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Get Test"
    assert len(data["checklist_items"]) == 2

    # Non-existent ID should return 404
    resp = await auth_client.get("/api/service-types/00000000-0000-0000-0000-000000000099")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_service_type(auth_client: AsyncClient):
    created = await _create_service_type(auth_client, name="Update Test")

    resp = await auth_client.patch(
        f"/api/service-types/{created['id']}",
        json={"base_price": 75.00, "description": "Updated", "is_active": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["base_price"] == "75.0"
    assert data["description"] == "Updated"
    assert data["is_active"] is False
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_update_checklist(auth_client: AsyncClient):
    created = await _create_service_type(auth_client, name="Checklist Test")
    assert len(created["checklist_items"]) == 2

    # Replace checklist with new items
    resp = await auth_client.put(
        f"/api/service-types/{created['id']}/checklist",
        json={
            "items": [
                {"name": "Mop floors", "sort_order": 1},
                {"name": "Dust furniture", "sort_order": 2},
                {"name": "Empty bins", "sort_order": 3},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["checklist_items"]) == 3
    names = [item["name"] for item in data["checklist_items"]]
    assert names == ["Mop floors", "Dust furniture", "Empty bins"]

    # Old items should be gone
    assert "Vacuum floors" not in names


@pytest.mark.asyncio
async def test_delete_service_type(auth_client: AsyncClient):
    created = await _create_service_type(auth_client, name="Delete Test")

    resp = await auth_client.delete(f"/api/service-types/{created['id']}")
    assert resp.status_code == 204

    # Should no longer appear in list
    list_resp = await auth_client.get("/api/service-types")
    ids = [st["id"] for st in list_resp.json()["items"]]
    assert created["id"] not in ids

    # GET should return 404
    get_resp = await auth_client.get(f"/api/service-types/{created['id']}")
    assert get_resp.status_code == 404
