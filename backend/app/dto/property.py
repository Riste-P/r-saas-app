from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field

from app.database.models.property import PropertyType

if TYPE_CHECKING:
    from app.database.models.property import Property


class ServiceBadgeItem(BaseModel):
    service_type_name: str
    effective_price: Decimal
    is_active: bool


def _compute_service_badges(
    prop: Property,
    parent_assignments: list | None = None,
) -> list[ServiceBadgeItem]:
    """Compute lightweight service badge data from eager-loaded relationships."""
    own = [a for a in prop.service_assignments if a.deleted_at is None]

    # No parent → direct assignments only
    if parent_assignments is None:
        return [
            ServiceBadgeItem(
                service_type_name=a.service_type.name,
                effective_price=a.custom_price if a.custom_price is not None else a.service_type.base_price,
                is_active=a.is_active,
            )
            for a in own
        ]

    # Has parent → merge parent + child overrides
    own_by_st = {a.service_type_id: a for a in own}
    badges: list[ServiceBadgeItem] = []

    for pa in parent_assignments:
        if not pa.is_active:
            continue
        override = own_by_st.get(pa.service_type_id)
        if override:
            eff_price = (
                override.custom_price
                if override.custom_price is not None
                else pa.custom_price
                if pa.custom_price is not None
                else pa.service_type.base_price
            )
            badges.append(ServiceBadgeItem(
                service_type_name=pa.service_type.name,
                effective_price=eff_price,
                is_active=override.is_active,
            ))
        else:
            eff_price = pa.custom_price if pa.custom_price is not None else pa.service_type.base_price
            badges.append(ServiceBadgeItem(
                service_type_name=pa.service_type.name,
                effective_price=eff_price,
                is_active=True,
            ))

    # Add child-only direct services (not from parent)
    parent_st_ids = {pa.service_type_id for pa in parent_assignments}
    for da in own:
        if da.service_type_id not in parent_st_ids:
            badges.append(ServiceBadgeItem(
                service_type_name=da.service_type.name,
                effective_price=da.custom_price if da.custom_price is not None else da.service_type.base_price,
                is_active=da.is_active,
            ))

    return badges


class CreatePropertyRequest(BaseModel):
    client_id: UUID | None = None
    parent_property_id: UUID | None = None
    property_type: PropertyType
    name: str
    address: str | None = None
    city: str | None = None
    notes: str | None = None
    number_of_units: int | None = Field(None, ge=1, le=100)


class UpdatePropertyRequest(BaseModel):
    client_id: UUID | None = None
    parent_property_id: UUID | None = None
    property_type: PropertyType | None = None
    name: str | None = None
    address: str | None = None
    city: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class PropertySummaryResponse(BaseModel):
    id: UUID
    name: str
    property_type: PropertyType
    address: str | None
    client_name: str | None
    is_active: bool
    services: list[ServiceBadgeItem]

    @classmethod
    def from_entity(
        cls,
        prop: Property,
        parent_assignments: list | None = None,
    ) -> PropertySummaryResponse:
        return cls(
            id=prop.id,
            name=prop.name,
            property_type=prop.property_type,
            address=prop.address,
            client_name=prop.client.name if prop.client else None,
            is_active=prop.is_active,
            services=_compute_service_badges(prop, parent_assignments),
        )


class PropertyResponse(BaseModel):
    id: UUID
    client_id: UUID | None
    client_name: str | None
    parent_property_id: UUID | None
    parent_property_name: str | None
    property_type: PropertyType
    name: str
    address: str | None
    city: str | None
    notes: str | None
    is_active: bool
    child_properties: list[PropertySummaryResponse]
    services: list[ServiceBadgeItem]
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, prop: Property) -> PropertyResponse:
        # Own active assignments (for badges + passing to children)
        own_assignments = [a for a in prop.service_assignments if a.deleted_at is None]

        return cls(
            id=prop.id,
            client_id=prop.client_id,
            client_name=prop.client.name if prop.client else None,
            parent_property_id=prop.parent_property_id,
            parent_property_name=prop.parent_property.name if prop.parent_property else None,
            property_type=prop.property_type,
            name=prop.name,
            address=prop.address,
            city=prop.city,
            notes=prop.notes,
            is_active=prop.is_active,
            child_properties=[
                PropertySummaryResponse.from_entity(child, parent_assignments=own_assignments)
                for child in prop.child_properties
                if child.deleted_at is None
            ],
            services=_compute_service_badges(prop),
            created_at=prop.created_at,
            updated_at=prop.updated_at,
        )
