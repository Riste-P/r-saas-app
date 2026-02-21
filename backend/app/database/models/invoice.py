import enum
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.invoice_item import InvoiceItem
    from app.database.models.payment import Payment
    from app.database.models.property import Property


class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class Invoice(Base, AuditMixin, TenantMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        Index(
            "uq_invoice_number_per_tenant",
            "tenant_id",
            "invoice_number",
            unique=True,
            postgresql_where="deleted_at IS NULL",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False, index=True
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status_enum"),
        nullable=False,
        default=InvoiceStatus.draft,
    )
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0
    )
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    property: Mapped["Property"] = relationship()
    items: Mapped[list["InvoiceItem"]] = relationship(
        back_populates="invoice", order_by="InvoiceItem.sort_order"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="invoice")
