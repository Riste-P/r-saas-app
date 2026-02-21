import pytest
from httpx import AsyncClient


async def _create_client(auth_client: AsyncClient, name: str = "Pay Test Client") -> dict:
    resp = await auth_client.post("/api/clients", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


async def _create_property(auth_client: AsyncClient, client_id: str, **overrides) -> dict:
    payload = {
        "client_id": client_id,
        "property_type": "house",
        "name": "Pay House",
        "address": "1 Pay St",
        **overrides,
    }
    resp = await auth_client.post("/api/properties", json=payload)
    assert resp.status_code == 201
    return resp.json()


async def _create_invoice(auth_client: AsyncClient, property_id: str, total: float = 100.0) -> dict:
    payload = {
        "property_id": property_id,
        "issue_date": "2026-02-01",
        "due_date": "2026-03-01",
        "items": [
            {"description": "Service", "quantity": 1, "unit_price": total},
        ],
    }
    resp = await auth_client.post("/api/invoices", json=payload)
    assert resp.status_code == 201
    return resp.json()


async def _create_payment(auth_client: AsyncClient, invoice_id: str, amount: float = 100.0, **overrides) -> dict:
    payload = {
        "invoice_id": invoice_id,
        "amount": amount,
        "payment_date": "2026-02-15",
        "payment_method": "bank_transfer",
        **overrides,
    }
    resp = await auth_client.post("/api/payments", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ── Create Payment ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_payment(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Create Pay Client")
    prop = await _create_property(auth_client, client["id"], name="Create Pay House")
    inv = await _create_invoice(auth_client, prop["id"], total=200.0)

    data = await _create_payment(auth_client, inv["id"], amount=150.0, reference="REF-001")
    assert data["invoice_id"] == inv["id"]
    assert data["invoice_number"] == inv["invoice_number"]
    assert float(data["amount"]) == 150.0
    assert data["payment_date"] == "2026-02-15"
    assert data["payment_method"] == "bank_transfer"
    assert data["reference"] == "REF-001"


@pytest.mark.asyncio
async def test_create_payment_auto_marks_paid(auth_client: AsyncClient):
    """When total payments >= invoice total, invoice is auto-marked as paid."""
    client = await _create_client(auth_client, "AutoPaid Client")
    prop = await _create_property(auth_client, client["id"], name="AutoPaid House")
    inv = await _create_invoice(auth_client, prop["id"], total=100.0)

    # Set invoice to sent first (so paid transition makes sense)
    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    # Pay full amount
    await _create_payment(auth_client, inv["id"], amount=100.0)

    # Invoice should now be paid
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "paid"
    assert resp.json()["paid_date"] is not None


@pytest.mark.asyncio
async def test_create_payment_partial_stays_unpaid(auth_client: AsyncClient):
    """Partial payment does not auto-mark invoice as paid."""
    client = await _create_client(auth_client, "Partial Pay Client")
    prop = await _create_property(auth_client, client["id"], name="Partial Pay House")
    inv = await _create_invoice(auth_client, prop["id"], total=200.0)

    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})
    await _create_payment(auth_client, inv["id"], amount=50.0)

    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "sent"  # Still sent, not paid


@pytest.mark.asyncio
async def test_create_payment_multiple_to_paid(auth_client: AsyncClient):
    """Multiple partial payments summing to total triggers auto-paid."""
    client = await _create_client(auth_client, "MultiPay Client")
    prop = await _create_property(auth_client, client["id"], name="MultiPay House")
    inv = await _create_invoice(auth_client, prop["id"], total=100.0)

    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    await _create_payment(auth_client, inv["id"], amount=40.0)
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "sent"

    await _create_payment(auth_client, inv["id"], amount=60.0)
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "paid"


@pytest.mark.asyncio
async def test_create_payment_invalid_invoice(auth_client: AsyncClient):
    resp = await auth_client.post("/api/payments", json={
        "invoice_id": "00000000-0000-0000-0000-000000000099",
        "amount": 50.0,
        "payment_date": "2026-02-15",
        "payment_method": "cash",
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_payment_various_methods(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Methods Client")
    prop = await _create_property(auth_client, client["id"], name="Methods House")
    inv = await _create_invoice(auth_client, prop["id"], total=500.0)

    for method in ["cash", "bank_transfer", "card", "other"]:
        data = await _create_payment(
            auth_client, inv["id"], amount=10.0, payment_method=method
        )
        assert data["payment_method"] == method


# ── List Payments ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_payments(auth_client: AsyncClient):
    client = await _create_client(auth_client, "List Pay Client")
    prop = await _create_property(auth_client, client["id"], name="List Pay House")
    inv = await _create_invoice(auth_client, prop["id"], total=500.0)

    await _create_payment(auth_client, inv["id"], amount=100.0)
    await _create_payment(auth_client, inv["id"], amount=200.0)

    resp = await auth_client.get("/api/payments")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_list_payments_filter_by_invoice(auth_client: AsyncClient):
    client = await _create_client(auth_client, "InvFilter Client")
    prop = await _create_property(auth_client, client["id"], name="InvFilter House")
    inv1 = await _create_invoice(auth_client, prop["id"], total=300.0)
    inv2 = await _create_invoice(auth_client, prop["id"], total=400.0)

    await _create_payment(auth_client, inv1["id"], amount=100.0)
    await _create_payment(auth_client, inv2["id"], amount=200.0)

    resp = await auth_client.get(f"/api/payments?invoice_id={inv1['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["invoice_id"] == inv1["id"]


# ── Delete Payment ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_payment(auth_client: AsyncClient):
    client = await _create_client(auth_client, "Delete Pay Client")
    prop = await _create_property(auth_client, client["id"], name="Delete Pay House")
    inv = await _create_invoice(auth_client, prop["id"], total=100.0)

    payment = await _create_payment(auth_client, inv["id"], amount=50.0)

    resp = await auth_client.delete(f"/api/payments/{payment['id']}")
    assert resp.status_code == 204

    # Payment should no longer appear in list for this invoice
    resp = await auth_client.get(f"/api/payments?invoice_id={inv['id']}")
    ids = [p["id"] for p in resp.json()["items"]]
    assert payment["id"] not in ids


@pytest.mark.asyncio
async def test_delete_payment_reverts_paid_status(auth_client: AsyncClient):
    """Deleting a payment that made an invoice 'paid' should revert to 'sent'."""
    client = await _create_client(auth_client, "Revert Pay Client")
    prop = await _create_property(auth_client, client["id"], name="Revert Pay House")
    inv = await _create_invoice(auth_client, prop["id"], total=100.0)

    await auth_client.patch(f"/api/invoices/{inv['id']}", json={"status": "sent"})

    # Pay full amount
    payment = await _create_payment(auth_client, inv["id"], amount=100.0)

    # Verify it's paid
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "paid"

    # Delete the payment
    resp = await auth_client.delete(f"/api/payments/{payment['id']}")
    assert resp.status_code == 204

    # Invoice should revert to sent
    resp = await auth_client.get(f"/api/invoices/{inv['id']}")
    assert resp.json()["status"] == "sent"
    assert resp.json()["paid_date"] is None


@pytest.mark.asyncio
async def test_delete_nonexistent_payment(auth_client: AsyncClient):
    resp = await auth_client.delete(
        "/api/payments/00000000-0000-0000-0000-000000000099"
    )
    assert resp.status_code == 404
