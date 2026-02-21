from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.invoice import Invoice
    from app.database.models.invoice_item import InvoiceItem


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class InvoiceItemRequest(BaseModel):
    service_type_id: UUID | None = None
    description: str
    quantity: Decimal = Decimal("1")
    unit_price: Decimal
    sort_order: int = 0


class CreateInvoiceRequest(BaseModel):
    property_id: UUID
    issue_date: date
    due_date: date
    period_start: date | None = None
    period_end: date | None = None
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    notes: str | None = None
    items: list[InvoiceItemRequest] = []


class UpdateInvoiceRequest(BaseModel):
    status: str | None = None
    issue_date: date | None = None
    due_date: date | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    notes: str | None = None
    paid_date: date | None = None


class GenerateInvoicesRequest(BaseModel):
    property_id: UUID
    issue_date: date
    due_date: date
    period_start: date | None = None
    period_end: date | None = None
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    notes: str | None = None


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------
class InvoiceItemResponse(BaseModel):
    id: UUID
    service_type_id: UUID | None
    description: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal
    sort_order: int

    @classmethod
    def from_entity(cls, item: InvoiceItem) -> InvoiceItemResponse:
        return cls(
            id=item.id,
            service_type_id=item.service_type_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total=item.total,
            sort_order=item.sort_order,
        )


class PaymentSummaryResponse(BaseModel):
    id: UUID
    amount: Decimal
    payment_date: date
    payment_method: str

    @classmethod
    def from_entity(cls, p: object) -> PaymentSummaryResponse:
        return cls(
            id=p.id,  # type: ignore[attr-defined]
            amount=p.amount,  # type: ignore[attr-defined]
            payment_date=p.payment_date,  # type: ignore[attr-defined]
            payment_method=p.payment_method.value,  # type: ignore[attr-defined]
        )


class InvoiceResponse(BaseModel):
    id: UUID
    property_id: UUID
    property_name: str
    client_name: str | None
    invoice_number: str
    status: str
    period_start: date | None
    period_end: date | None
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    issue_date: date
    due_date: date
    paid_date: date | None
    notes: str | None
    items: list[InvoiceItemResponse]
    payments: list[PaymentSummaryResponse]
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, inv: Invoice) -> InvoiceResponse:
        return cls(
            id=inv.id,
            property_id=inv.property_id,
            property_name=inv.property.name,
            client_name=inv.property.client.name if inv.property.client else None,
            invoice_number=inv.invoice_number,
            status=inv.status.value,
            period_start=inv.period_start,
            period_end=inv.period_end,
            subtotal=inv.subtotal,
            discount=inv.discount,
            tax=inv.tax,
            total=inv.total,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            paid_date=inv.paid_date,
            notes=inv.notes,
            items=[InvoiceItemResponse.from_entity(i) for i in inv.items],
            payments=[PaymentSummaryResponse.from_entity(p) for p in inv.payments if p.deleted_at is None],
            created_at=inv.created_at,
            updated_at=inv.updated_at,
        )


class InvoiceListResponse(BaseModel):
    id: UUID
    property_id: UUID
    property_name: str
    parent_property_name: str | None
    client_name: str | None
    invoice_number: str
    status: str
    total: Decimal
    issue_date: date
    due_date: date
    paid_date: date | None
    created_at: datetime

    @classmethod
    def from_entity(cls, inv: Invoice) -> InvoiceListResponse:
        parent = inv.property.parent_property
        return cls(
            id=inv.id,
            property_id=inv.property_id,
            property_name=inv.property.name,
            parent_property_name=parent.name if parent else None,
            client_name=inv.property.client.name if inv.property.client else None,
            invoice_number=inv.invoice_number,
            status=inv.status.value,
            total=inv.total,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            paid_date=inv.paid_date,
            created_at=inv.created_at,
        )
