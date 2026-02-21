import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.invoice import Invoice
    from app.database.models.service_type import ServiceType


class InvoiceItem(Base, AuditMixin, TenantMixin):
    __tablename__ = "invoice_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True
    )
    service_type_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_types.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    invoice: Mapped["Invoice"] = relationship(back_populates="items")
    service_type: Mapped[Optional["ServiceType"]] = relationship()
