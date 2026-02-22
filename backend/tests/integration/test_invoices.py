import pytest
from httpx import AsyncClient


async def _create_client(auth_client: AsyncClient, name: str = "Inv Test Client") -> dict:
    resp = await auth_client.post("/api/clients", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


async def _create_property(auth_client: AsyncClient, client_id: str, **overrides) -> dict:
    payload = {
        "client_id": client_id,
        "property_type": "house",
        "name": "Inv House",
        "address": "1 Inv St",
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


async def _create_invoice(auth_client: AsyncClient, property_id: str, **overrides) -> dict:
    payload = {
        "property_id": property_id,
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
        "items": [
            {
                "description": "Cleaning service",
                "quantity": 1,
                "unit_price": 100.0,
            }
        ],
        **overrides,
    }
    resp = await auth_client.post("/api/invoices", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ── Create Invoice ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Create Inv Client")
    prop = await _create_property(auth_client, client["id"], name="Create Inv House")

    data = await _create_invoice(auth_client, prop["id"])
    assert data["property_id"] == prop["id"]
    assert data["property_name"] == "Create Inv House"
    assert data["client_name"] == "Create Inv Client"
    assert data["status"] == "draft"
    assert data["invoice_number"].startswith("INV-")
    assert data["issue_date"] == "2026-02-01"
    assert data["due_date"] == "2026-03-01"
    assert len(data["items"]) == 1
    assert data["items"][0]["description"] == "Cleaning service"
    assert float(data["subtotal"]) == 100.0
    assert float(data["discount"]) == 0
    assert float(data["tax"]) == 0
    assert float(data["total"]) == 100.0
    assert data["payments"] == []


@pytest.mark.asyncio
async def test_create_invoice_with_multiple_items(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Multi Item Client")
    prop = await _create_property(auth_client, client["id"], name="Multi Item House")

    data = await _create_invoice(
        auth_client,
        prop["id"],
        items=[
            {"description": "Cleaning", "quantity": 2, "unit_price": 50.0},
            {"description": "Deep clean", "quantity": 1, "unit_price": 80.0},
        ],
        discount=10.0,
        tax=15.0,
    )
    # subtotal = (2*50) + (1*80) = 180
    assert float(data["subtotal"]) == 180.0
    assert float(data["discount"]) == 10.0
    assert float(data["tax"]) == 15.0
    # total = 180 - 10 + 15 = 185
    assert float(data["total"]) == 185.0
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_create_invoice_invalid_property(auth_client: AsyncClient):
    resp = await auth_client.post("/api/invoices", json={
        "property_id": "00000000-0000-0000-0000-000000000099",
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
        "items": [{"description": "Test", "quantity": 1, "unit_price": 10.0}],
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_invoice_sequential_numbers(auth_client: AsyncClient):
    """Invoice numbers increment sequentially within a month."""
    client = await _create_client(auth_client, "SeqNum Client")
    prop = await _create_property(auth_client, client["id"], name="SeqNum House")

    inv1 = await _create_invoice(auth_client, prop["id"])
    inv2 = await _create_invoice(auth_client, prop["id"])

    # Both should start with same prefix
    prefix1 = inv1["invoice_number"].rsplit("-", 1)[0]
    prefix2 = inv2["invoice_number"].rsplit("-", 1)[0]
    assert prefix1 == prefix2

    # Second number should be higher than first
    seq1 = int(inv1["invoice_number"].split("-")[-1])
    seq2 = int(inv2["invoice_number"].split("-")[-1])
    assert seq2 == seq1 + 1


# ── Get Invoice ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Get Inv Client")
    prop = await _create_property(auth_client, client["id"], name="Get Inv House")
    inv = await _create_invoice(auth_client, prop["id"], notes="test note")

    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == inv["id"]
    assert data["notes"] == "test note"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_get_invoice_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/api/invoices/00000000-0000-0000-0000-000000000099")
    assert resp.status_code == 404


# ── List Invoices ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_invoices(auth_client: AsyncClient):
    client = await _create_client(auth_client, "List Inv Client")
    prop = await _create_property(auth_client, client["id"], name="List Inv House")
    await _create_invoice(auth_client, prop["id"])
    await _create_invoice(auth_client, prop["id"])

    resp = await auth_client.get("/api/invoices")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_invoices_filter_by_status(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Status Filter Client")
    prop = await _create_property(auth_client, client["id"], name="Status Filter House")
    inv = await _create_invoice(auth_client, prop["id"])

    # Update one to "sent"
    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    resp = await auth_client.get("/api/invoices?status=sent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["status"] == "sent"


@pytest.mark.asyncio
async def test_list_invoices_filter_by_client(auth_client: AsyncClient):
    client = await _create_client(auth_client, "ClientFilter Client")
    prop = await _create_property(auth_client, client["id"], name="ClientFilter House")
    await _create_invoice(auth_client, prop["id"])

    resp = await auth_client.get(f"/api/invoices?client_id={client['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


# ── Update Invoice ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Update Inv Client")
    prop = await _create_property(auth_client, client["id"], name="Update Inv House")
    inv = await _create_invoice(auth_client, prop["id"])

    resp = await auth_client.patch(f"/api/invoices/{inv['id']}", json={
        "status": "sent",
        "notes": "Updated note",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "sent"
    assert data["notes"] == "Updated note"
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_update_invoice_recalculates_total(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Recalc Client")
    prop = await _create_property(auth_client, client["id"], name="Recalc House")
    inv = await _create_invoice(auth_client, prop["id"])  # subtotal=100, total=100

    resp = await auth_client.patch(f"/api/invoices/{inv['id']}", json={
        "discount": 20.0,
        "tax": 5.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert float(data["discount"]) == 20.0
    assert float(data["tax"]) == 5.0
    # total = subtotal(100) - discount(20) + tax(5) = 85
    assert float(data["total"]) == 85.0


# ── Delete Invoice ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_draft_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Delete Draft Client")
    prop = await _create_property(auth_client, client["id"], name="Delete Draft House")
    inv = await _create_invoice(auth_client, prop["id"])

    resp = await auth_client.delete(f"/api/invoices/{inv['id']}")
    assert resp.status_code == 204

    # Should return 404
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_cancelled_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Delete Cancel Client")
    prop = await _create_property(auth_client, client["id"], name="Delete Cancel House")
    inv = await _create_invoice(auth_client, prop["id"])

    # Set to cancelled first
    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "cancelled"})

    resp = await auth_client.delete(f"/api/invoices/{inv['id']}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_sent_invoice_fails(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Delete Sent Client")
    prop = await _create_property(auth_client, client["id"], name="Delete Sent House")
    inv = await _create_invoice(auth_client, prop["id"])

    # Set to sent
    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    resp = await auth_client.delete(f"/api/invoices/{inv['id']}")
    assert resp.status_code == 400


# ── Generate Invoices ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_invoices_for_building(auth_client: AsyncClient):
    """Generate invoices creates one per active child unit."""
    client = await _create_client(auth_client, "Generate Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="Gen Building", address="10 Gen St"
    )
    apt1 = await _create_property(
        auth_client, client["id"], property_type="unit", name="Gen Apt 1",
        address="10 Gen St, 1A", parent_property_id=building["id"],
    )
    apt2 = await _create_property(
        auth_client, client["id"], property_type="unit", name="Gen Apt 2",
        address="10 Gen St, 2B", parent_property_id=building["id"],
    )

    st = await _create_service_type(auth_client, "Gen Cleaning", base_price=80.0)
    await _assign_service(auth_client, building["id"], st["id"])

    resp = await auth_client.post("/api/invoices/generate", json={
        "property_id": building["id"],
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 2  # One per apartment

    property_names = {inv["property_name"] for inv in data}
    assert "Gen Apt 1" in property_names
    assert "Gen Apt 2" in property_names

    # Each invoice should have one item with the service price
    for inv in data:
        assert len(inv["items"]) == 1
        assert float(inv["items"][0]["unit_price"]) == 80.0
        assert float(inv["total"]) == 80.0


@pytest.mark.asyncio
async def test_generate_invoices_standalone_property(auth_client: AsyncClient):
    """Standalone property (no children) generates one invoice for itself."""
    client = await _create_client(auth_client, "Gen Standalone Client")
    prop = await _create_property(auth_client, client["id"], name="Gen Standalone House")
    st = await _create_service_type(auth_client, "Gen Standalone Svc", base_price=100.0)
    await _assign_service(auth_client, prop["id"], st["id"])

    resp = await auth_client.post("/api/invoices/generate", json={
        "property_id": prop["id"],
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert data[0]["property_name"] == "Gen Standalone House"
    assert float(data[0]["total"]) == 100.0


@pytest.mark.asyncio
async def test_generate_invoices_respects_child_opt_out(auth_client: AsyncClient):
    """Children that opted out of a service are skipped."""
    client = await _create_client(auth_client, "Gen OptOut Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="Gen OptOut Building", address="5 St"
    )
    apt1 = await _create_property(
        auth_client, client["id"], property_type="unit", name="Gen OptOut Apt 1",
        address="5 St, 1A", parent_property_id=building["id"],
    )
    apt2 = await _create_property(
        auth_client, client["id"], property_type="unit", name="Gen OptOut Apt 2",
        address="5 St, 2B", parent_property_id=building["id"],
    )

    st = await _create_service_type(auth_client, "Gen OptOut Svc")
    await _assign_service(auth_client, building["id"], st["id"])
    # apt2 opts out
    await _assign_service(auth_client, apt2["id"], st["id"], is_active=False)

    resp = await auth_client.post("/api/invoices/generate", json={
        "property_id": building["id"],
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
    })
    assert resp.status_code == 201
    data = resp.json()
    # Only apt1 should get an invoice (apt2 opted out of the only service)
    assert len(data) == 1
    assert data[0]["property_name"] == "Gen OptOut Apt 1"


@pytest.mark.asyncio
async def test_generate_invoices_with_child_price_override(auth_client: AsyncClient):
    """Child price override is reflected in generated invoice."""
    client = await _create_client(auth_client, "Gen Override Client")
    building = await _create_property(
        auth_client, client["id"], property_type="building", name="Gen Override Building", address="6 St"
    )
    apt = await _create_property(
        auth_client, client["id"], property_type="unit", name="Gen Override Apt",
        address="6 St, 1A", parent_property_id=building["id"],
    )

    st = await _create_service_type(auth_client, "Gen Override Svc", base_price=100.0)
    await _assign_service(auth_client, building["id"], st["id"])
    await _assign_service(auth_client, apt["id"], st["id"], custom_price=60.0)

    resp = await auth_client.post("/api/invoices/generate", json={
        "property_id": building["id"],
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert float(data[0]["items"][0]["unit_price"]) == 60.0
    assert float(data[0]["total"]) == 60.0


@pytest.mark.asyncio
async def test_generate_invoices_with_discount_and_tax(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Gen DT Client")
    prop = await _create_property(auth_client, client["id"], name="Gen DT House")
    st = await _create_service_type(auth_client, "Gen DT Svc", base_price=200.0)
    await _assign_service(auth_client, prop["id"], st["id"])

    resp = await auth_client.post("/api/invoices/generate", json={
        "property_id": prop["id"],
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
        "discount": 25.0,
        "tax": 10.0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    # total = 200 - 25 + 10 = 185
    assert float(data[0]["total"]) == 185.0


# ── Mark Overdue ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mark_overdue(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Overdue Client")
    prop = await _create_property(auth_client, client["id"], name="Overdue House")

    inv = await _create_invoice(
        auth_client, prop["id"],
        issue_date="2025-01-01",
        due_date="2025-01-15",  # Past due
    )
    # Set to sent (only sent invoices can be marked overdue)
    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    resp = await auth_client.post("/api/invoices/mark-overdue")
    assert resp.status_code == 200
    data = resp.json()
    assert data["marked_overdue"] >= 1

    # Verify the invoice is now overdue
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "overdue"


@pytest.mark.asyncio
async def test_mark_overdue_ignores_drafts(auth_client: AsyncClient):
    """Draft invoices should not be marked overdue even if past due."""
    client = await _create_client(auth_client, "Overdue Draft Client")
    prop = await _create_property(auth_client, client["id"], name="Overdue Draft House")

    inv = await _create_invoice(
        auth_client, prop["id"],
        issue_date="2025-01-01",
        due_date="2025-01-15",
    )
    # Leave as draft

    await auth_client.post("/api/invoices/mark-overdue")

    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "draft"  # Still draft
