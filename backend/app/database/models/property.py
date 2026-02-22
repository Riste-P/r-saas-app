import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base, TenantMixin

if TYPE_CHECKING:
    from app.database.models.client import Client
    from app.database.models.property_service_type import PropertyServiceType


class PropertyType(str, enum.Enum):
    house = "house"
    apartment = "apartment"
    building = "building"
    commercial = "commercial"
    unit = "unit"


class Property(Base, AuditMixin, TenantMixin):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clients.id"), nullable=True, index=True
    )
    parent_property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=True, index=True
    )
    property_type: Mapped[PropertyType] = mapped_column(
        Enum(PropertyType, name="property_type_enum"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    client: Mapped[Optional["Client"]] = relationship(back_populates="properties")
    parent_property: Mapped[Optional["Property"]] = relationship(
        back_populates="child_properties", remote_side=[id]
    )
    child_properties: Mapped[list["Property"]] = relationship(
        back_populates="parent_property"
    )
    service_assignments: Mapped[list["PropertyServiceType"]] = relationship(
        back_populates="property"
    )
