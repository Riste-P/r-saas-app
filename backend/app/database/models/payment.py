import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.invoice import Invoice


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    bank_transfer = "bank_transfer"
    card = "card"
    other = "other"


class Payment(Base, AuditMixin, TenantMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method_enum"), nullable=False
    )
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    invoice: Mapped["Invoice"] = relationship(back_populates="payments")
