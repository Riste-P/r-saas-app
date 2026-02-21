from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.payment import Payment


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
class CreatePaymentRequest(BaseModel):
    invoice_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: str
    reference: str | None = None
    notes: str | None = None


class UpdatePaymentRequest(BaseModel):
    amount: Decimal | None = None
    payment_date: date | None = None
    payment_method: str | None = None
    reference: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------
class PaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    invoice_number: str
    amount: Decimal
    payment_date: date
    payment_method: str
    reference: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, p: Payment) -> PaymentResponse:
        return cls(
            id=p.id,
            invoice_id=p.invoice_id,
            invoice_number=p.invoice.invoice_number,
            amount=p.amount,
            payment_date=p.payment_date,
            payment_method=p.payment_method.value,
            reference=p.reference,
            notes=p.notes,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
