import pytest
from httpx import AsyncClient


async def _create_client(auth_client: AsyncClient, name: str = "Prop Test Client") -> dict:
    resp = await auth_client.post("/api/clients", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


async def _create_property(auth_client: AsyncClient, client_id: str, **overrides) -> dict:
    payload = {
        "client_id": client_id,
        "property_type": "house",
        "name": "Default House",
        "address": "1 Test St",
        **overrides,
    }
    resp = await auth_client.post("/api/properties", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_property(auth_client: AsyncClient):
    client = await _create_client(auth_client, name="Create Prop Client")
    data = await _create_property(
        auth_client, client["id"],
        name="Beach House",
        address="99 Ocean Dr",
        city="Miami",
        size_sqm=200,
        num_rooms=4,
    )
    assert data["name"] == "Beach House"
    assert data["property_type"] == "house"
    assert data["client_name"] == "Create Prop Client"
    assert data["city"] == "Miami"
    assert data["size_sqm"] == "200"
    assert data["num_rooms"] == 4
    assert data["is_active"] is True
    assert data["child_properties"] == []

    # Invalid client should fail
    resp = await auth_client.post("/api/properties", json={
        "client_id": "00000000-0000-0000-0000-000000000099",
        "property_type": "house",
        "name": "Fail",
        "address": "Nowhere",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_apartment_with_building(auth_client: AsyncClient):
    client = await _create_client(auth_client, name="Building Client")

    # Create building
    building = await _create_property(
        auth_client, client["id"],
        property_type="building", name="Tower A", address="10 High St",
    )

    # Create apartment under building
    apt = await _create_property(
        auth_client, client["id"],
        property_type="apartment", name="Apt 1A", address="10 High St, 1A",
        parent_property_id=building["id"], floor="1",
        contact_name="Tenant Joe", contact_phone="+111",
    )
    assert apt["parent_property_id"] == building["id"]
    assert apt["floor"] == "1"
    assert apt["contact_name"] == "Tenant Joe"

    # Building should list apartment as child
    resp = await auth_client.get(f"/api/properties/{building['id']}")
    assert resp.status_code == 200
    children = resp.json()["child_properties"]
    assert len(children) == 1
    assert children[0]["name"] == "Apt 1A"

    # Apartment under a house should fail (parent must be building)
    house = await _create_property(
        auth_client, client["id"], name="A House", address="5 Low St",
    )
    resp = await auth_client.post("/api/properties", json={
        "client_id": client["id"],
        "property_type": "apartment",
        "name": "Bad Apt",
        "address": "Nowhere",
        "parent_property_id": house["id"],
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_properties_with_filters(auth_client: AsyncClient):
    client = await _create_client(auth_client, name="Filter Client")
    await _create_property(auth_client, client["id"], name="House 1", property_type="house")
    await _create_property(auth_client, client["id"], name="House 2", property_type="house")
    await _create_property(auth_client, client["id"], name="Office 1", property_type="commercial")

    # No filter
    resp = await auth_client.get("/api/properties")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3

    # Filter by property_type
    resp = await auth_client.get("/api/properties?property_type=house")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()["items"]]
    assert "House 1" in names
    assert "House 2" in names
    assert "Office 1" not in names

    # Filter by client_id
    resp = await auth_client.get(f"/api/properties?client_id={client['id']}")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3


@pytest.mark.asyncio
async def test_update_property(auth_client: AsyncClient):
    client = await _create_client(auth_client, name="Update Prop Client")
    prop = await _create_property(auth_client, client["id"], name="Old Name")

    resp = await auth_client.patch(
        f"/api/properties/{prop['id']}",
        json={"name": "New Name", "num_rooms": 3, "is_active": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["num_rooms"] == 3
    assert data["is_active"] is False
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_delete_property(auth_client: AsyncClient):
    client = await _create_client(auth_client, name="Delete Prop Client")

    # Create building with apartment
    building = await _create_property(
        auth_client, client["id"],
        property_type="building", name="Del Tower", address="1 Del St",
    )
    apt = await _create_property(
        auth_client, client["id"],
        property_type="apartment", name="Del Apt", address="1 Del St, 1A",
        parent_property_id=building["id"],
    )

    # Delete building should cascade to apartment
    resp = await auth_client.delete(f"/api/properties/{building['id']}")
    assert resp.status_code == 204

    assert (await auth_client.get(f"/api/properties/{building['id']}")).status_code == 404
    assert (await auth_client.get(f"/api/properties/{apt['id']}")).status_code == 404
