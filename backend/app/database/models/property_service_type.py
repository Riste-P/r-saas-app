import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Index, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.property import Property
    from app.database.models.service_type import ServiceType


class PropertyServiceType(Base, AuditMixin, TenantMixin):
    __tablename__ = "property_service_types"
    __table_args__ = (
        Index(
            "uq_property_service_type_active",
            "property_id",
            "service_type_id",
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
    service_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_types.id"), nullable=False, index=True
    )
    custom_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    property: Mapped["Property"] = relationship()
    service_type: Mapped["ServiceType"] = relationship()
