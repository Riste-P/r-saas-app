import pytest
from httpx import AsyncClient


async def _create_client(auth_client: AsyncClient, name: str = "PST Test Client") -> dict:
    resp = await auth_client.post("/api/clients", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


async def _create_property(auth_client: AsyncClient, client_id: str, **overrides) -> dict:
    payload = {
        "client_id": client_id,
        "property_type": "house",
        "name": "Test House",
        "address": "1 Test St",
        **overrides,
    }
    resp = await auth_client.post("/api/properties", json=payload)
    assert resp.status_code == 201
    return resp.json()


async def _create_service_type(auth_client: AsyncClient, name: str, base_price: float = 50.0) -> dict:
    resp = await auth_client.post("/api/service-types", json={
        "name": name,
        "base_price": base_price,
        "estimated_duration_minutes": 60,
    })
    assert resp.status_code == 201
    return resp.json()


async def _assign_service(
    auth_client: AsyncClient, property_id: str, service_type_id: str, **overrides
) -> dict:
    payload = {
        "property_id": property_id,
        "service_type_id": service_type_id,
        **overrides,
    }
    resp = await auth_client.post("/api/property-service-types", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ── Assign ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assign_service(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Assign Client")
    prop = await _create_property(auth_client, client["id"], name="Assign House")
    st = await _create_service_type(auth_client, "Assign Cleaning")

    data = await _assign_service(auth_client, prop["id"], st["id"])
    assert data["property_id"] == prop["id"]
    assert data["service_type_id"] == st["id"]
    assert data["service_type_name"] == "Assign Cleaning"
    assert data["custom_price"] is None
    assert float(data["effective_price"]) == 50.0
    assert data["is_active"] is True
    assert data["is_inherited"] is False


@pytest.mark.asyncio
async def test_assign_service_with_custom_price(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Custom Price Client")
    prop = await _create_property(auth_client, client["id"], name="Custom House")
    st = await _create_service_type(auth_client, "Custom Cleaning", base_price=80.0)

    data = await _assign_service(auth_client, prop["id"], st["id"], custom_price=65.0)
    assert float(data["custom_price"]) == 65.0
    assert float(data["effective_price"]) == 65.0


@pytest.mark.asyncio
async def test_assign_service_with_inactive(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Inactive Client")
    prop = await _create_property(auth_client, client["id"], name="Inactive House")
    st = await _create_service_type(auth_client, "Inactive Cleaning")

    data = await _assign_service(auth_client, prop["id"], st["id"], is_active=False)
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_assign_duplicate_fails(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Dup Client")
    prop = await _create_property(auth_client, client["id"], name="Dup House")
    st = await _create_service_type(auth_client, "Dup Cleaning")

    await _assign_service(auth_client, prop["id"], st["id"])

    # Second assignment should fail
    resp = await auth_client.post("/api/property-service-types", json={
        "property_id": prop["id"],
        "service_type_id": st["id"],
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_assign_invalid_property_fails(auth_client: AsyncClient):
    st = await _create_service_type(auth_client, "Orphan Cleaning")
    resp = await auth_client.post("/api/property-service-types", json={
        "property_id": "00000000-0000-0000-0000-000000000099",
        "service_type_id": st["id"],
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_assign_invalid_service_type_fails(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Bad ST Client")
    prop = await _create_property(auth_client, client["id"], name="Bad ST House")
    resp = await auth_client.post("/api/property-service-types", json={
        "property_id": prop["id"],
        "service_type_id": "00000000-0000-0000-0000-000000000099",
    })
    assert resp.status_code == 404


# ── Bulk Assign ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bulk_assign(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Bulk Client")
    prop = await _create_property(auth_client, client["id"], name="Bulk House")
    st1 = await _create_service_type(auth_client, "Bulk Svc 1")
    st2 = await _create_service_type(auth_client, "Bulk Svc 2")

    resp = await auth_client.post("/api/property-service-types/bulk", json={
        "property_id": prop["id"],
        "service_type_ids": [st1["id"], st2["id"]],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2
    names = {d["service_type_name"] for d in data}
    assert names == {"Bulk Svc 1", "Bulk Svc 2"}


@pytest.mark.asyncio
async def test_bulk_assign_skips_existing(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Bulk Skip Client")
    prop = await _create_property(auth_client, client["id"], name="Bulk Skip House")
    st1 = await _create_service_type(auth_client, "BulkSkip 1")
    st2 = await _create_service_type(auth_client, "BulkSkip 2")

    # Pre-assign one
    await _assign_service(auth_client, prop["id"], st1["id"])

    # Bulk assign both — should skip the already-assigned one
    resp = await auth_client.post("/api/property-service-types/bulk", json={
        "property_id": prop["id"],
        "service_type_ids": [st1["id"], st2["id"]],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2  # Returns all assignments


# ── List Assignments ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_assignments(auth_client: AsyncClient):
    client = await _create_client(auth_client, "List Client")
    prop = await _create_property(auth_client, client["id"], name="List House")
    st1 = await _create_service_type(auth_client, "List Svc 1")
    st2 = await _create_service_type(auth_client, "List Svc 2")

    await _assign_service(auth_client, prop["id"], st1["id"])
    await _assign_service(auth_client, prop["id"], st2["id"])

    resp = await auth_client.get(f"/api/property-service-types?property_id={prop['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


# ── Update Assignment ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_assignment(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Update Assign Client")
    prop = await _create_property(auth_client, client["id"], name="Update House")
    st = await _create_service_type(auth_client, "Update Svc", base_price=100.0)

    assignment = await _assign_service(auth_client, prop["id"], st["id"])

    # Update custom price
    resp = await auth_client.patch(
        f"/api/property-service-types/{assignment['id']}",
        json={"custom_price": 75.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["custom_price"]) == 75.0
    assert float(data["effective_price"]) == 75.0

    # Update is_active
    resp = await auth_client.patch(
        f"/api/property-service-types/{assignment['id']}",
        json={"is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_update_assignment_clear_custom_price(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Clear Price Client")
    prop = await _create_property(auth_client, client["id"], name="Clear Price House")
    st = await _create_service_type(auth_client, "Clear Price Svc", base_price=90.0)

    assignment = await _assign_service(auth_client, prop["id"], st["id"], custom_price=50.0)
    assert float(assignment["effective_price"]) == 50.0

    # Clear custom_price by sending null
    resp = await auth_client.patch(
        f"/api/property-service-types/{assignment['id']}",
        json={"custom_price": None},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["custom_price"] is None
    assert float(data["effective_price"]) == 90.0  # Falls back to base_price


@pytest.mark.asyncio
async def test_update_nonexistent_assignment(auth_client: AsyncClient):
    resp = await auth_client.patch(
        "/api/property-service-types/00000000-0000-0000-0000-000000000099",
        json={"custom_price": 10.0},
    )
    assert resp.status_code == 404


# ── Remove Assignment ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_parent_assignment_soft_deletes(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Remove Parent Client")
    prop = await _create_property(auth_client, client["id"], name="Remove Parent House")
    st = await _create_service_type(auth_client, "Remove Parent Svc")

    assignment = await _assign_service(auth_client, prop["id"], st["id"])

    resp = await auth_client.delete(f"/api/property-service-types/{assignment['id']}")
    assert resp.status_code == 204

    # Should no longer appear in list
    resp = await auth_client.get(f"/api/property-service-types?property_id={prop['id']}")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_remove_child_override_hard_deletes(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Remove Override Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="Override Building", address="1 St"
    )
    apt = await _create_property(
        auth_client, client["id"], property_type="unit", name="Override Apt",
        address="1 St, 1A", parent_property_id=building["id"],
    )
    st = await _create_service_type(auth_client, "Override Svc")

    # Assign to building
    await _assign_service(auth_client, building["id"], st["id"])

    # Create child override
    override = await _assign_service(auth_client, apt["id"], st["id"], custom_price=30.0)

    # Remove override
    resp = await auth_client.delete(f"/api/property-service-types/{override['id']}")
    assert resp.status_code == 204

    # Child should still see inherited service via effective endpoint
    resp = await auth_client.get(f"/api/property-service-types/effective?property_id={apt['id']}")
    assert resp.status_code == 200
    effective = resp.json()
    assert len(effective) == 1
    assert effective[0]["is_inherited"] is True
    assert effective[0]["override_id"] is None


@pytest.mark.asyncio
async def test_remove_nonexistent_assignment(auth_client: AsyncClient):
    resp = await auth_client.delete(
        "/api/property-service-types/00000000-0000-0000-0000-000000000099"
    )
    assert resp.status_code == 404


# ── Effective Services ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_effective_services_standalone(auth_client: AsyncClient):
    """Standalone property shows its own direct assignments."""
    client = await _create_client(auth_client, "Effective Standalone Client")
    prop = await _create_property(auth_client, client["id"], name="Effective House")
    st = await _create_service_type(auth_client, "Effective Svc", base_price=70.0)

    await _assign_service(auth_client, prop["id"], st["id"], custom_price=55.0)

    resp = await auth_client.get(f"/api/property-service-types/effective?property_id={prop['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["service_type_name"] == "Effective Svc"
    assert float(data[0]["effective_price"]) == 55.0
    assert data[0]["is_inherited"] is False
    assert data[0]["is_active"] is True


@pytest.mark.asyncio
async def test_effective_services_inherited(auth_client: AsyncClient):
    """Child inherits parent's services."""
    client = await _create_client(auth_client, "Inherit Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="Inherit Building", address="2 St"
    )
    apt = await _create_property(
        auth_client, client["id"], property_type="unit", name="Inherit Apt",
        address="2 St, 1A", parent_property_id=building["id"],
    )
    st = await _create_service_type(auth_client, "Inherit Svc", base_price=60.0)

    await _assign_service(auth_client, building["id"], st["id"])

    # Child should inherit
    resp = await auth_client.get(f"/api/property-service-types/effective?property_id={apt['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["is_inherited"] is True
    assert float(data[0]["effective_price"]) == 60.0
    assert data[0]["override_id"] is None


@pytest.mark.asyncio
async def test_effective_services_child_override_price(auth_client: AsyncClient):
    """Child override changes effective price."""
    client = await _create_client(auth_client, "Override Price Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="OverPrice Building", address="3 St"
    )
    apt = await _create_property(
        auth_client, client["id"], property_type="unit", name="OverPrice Apt",
        address="3 St, 1A", parent_property_id=building["id"],
    )
    st = await _create_service_type(auth_client, "OverPrice Svc", base_price=100.0)

    await _assign_service(auth_client, building["id"], st["id"])
    override = await _assign_service(auth_client, apt["id"], st["id"], custom_price=40.0)

    resp = await auth_client.get(f"/api/property-service-types/effective?property_id={apt['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert float(data[0]["effective_price"]) == 40.0
    assert data[0]["is_inherited"] is True
    assert data[0]["override_id"] == override["id"]


@pytest.mark.asyncio
async def test_effective_services_child_opt_out(auth_client: AsyncClient):
    """Child can opt out of inherited service by setting is_active=false."""
    client = await _create_client(auth_client, "OptOut Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="OptOut Building", address="4 St"
    )
    apt = await _create_property(
        auth_client, client["id"], property_type="unit", name="OptOut Apt",
        address="4 St, 1A", parent_property_id=building["id"],
    )
    st = await _create_service_type(auth_client, "OptOut Svc")

    await _assign_service(auth_client, building["id"], st["id"])
    await _assign_service(auth_client, apt["id"], st["id"], is_active=False)

    resp = await auth_client.get(f"/api/property-service-types/effective?property_id={apt['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["is_active"] is False
