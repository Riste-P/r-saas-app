import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.client import Client


class PropertyType(str, enum.Enum):
    house = "house"
    apartment = "apartment"
    building = "building"
    commercial = "commercial"


class Property(Base, AuditMixin, TenantMixin):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True
    )
    parent_property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True, index=True
    )
    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType, name="property_type_enum"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    size_sqm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    num_rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    access_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    client: Mapped["Client"] = relationship(back_populates="properties")
    parent_property: Mapped[Optional["Property"]] = relationship(
        back_populates="child_properties", remote_side=[id]
    )
    child_properties: Mapped[list["Property"]] = relationship(
        back_populates="parent_property"
    )
