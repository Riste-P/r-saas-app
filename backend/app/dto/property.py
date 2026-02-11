from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

from app.database.models.property import PropertyType

if TYPE_CHECKING:
    from app.database.models.property import Property


class CreatePropertyRequest(BaseModel):
    client_id: UUID
    parent_property_id: UUID | None = None
    property_type: PropertyType
    name: str
    address: str
    city: str | None = None
    postal_code: str | None = None
    size_sqm: Decimal | None = None
    num_rooms: int | None = None
    floor: str | None = None
    access_instructions: str | None = None
    key_code: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None


class UpdatePropertyRequest(BaseModel):
    client_id: UUID | None = None
    parent_property_id: UUID | None = None
    property_type: PropertyType | None = None
    name: str | None = None
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    size_sqm: Decimal | None = None
    num_rooms: int | None = None
    floor: str | None = None
    access_instructions: str | None = None
    key_code: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    is_active: bool | None = None


class PropertySummaryResponse(BaseModel):
    id: UUID
    name: str
    property_type: PropertyType
    address: str

    @classmethod
    def from_entity(cls, prop: Property) -> PropertySummaryResponse:
        return cls(
            id=prop.id,
            name=prop.name,
            property_type=prop.property_type,
            address=prop.address,
        )


class PropertyResponse(BaseModel):
    id: UUID
    client_id: UUID
    client_name: str
    parent_property_id: UUID | None
    property_type: PropertyType
    name: str
    address: str
    city: str | None
    postal_code: str | None
    size_sqm: Decimal | None
    num_rooms: int | None
    floor: str | None
    access_instructions: str | None
    key_code: str | None
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    is_active: bool
    child_properties: list[PropertySummaryResponse]
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, prop: Property) -> PropertyResponse:
        return cls(
            id=prop.id,
            client_id=prop.client_id,
            client_name=prop.client.name,
            parent_property_id=prop.parent_property_id,
            property_type=prop.property_type,
            name=prop.name,
            address=prop.address,
            city=prop.city,
            postal_code=prop.postal_code,
            size_sqm=prop.size_sqm,
            num_rooms=prop.num_rooms,
            floor=prop.floor,
            access_instructions=prop.access_instructions,
            key_code=prop.key_code,
            contact_name=prop.contact_name,
            contact_phone=prop.contact_phone,
            contact_email=prop.contact_email,
            is_active=prop.is_active,
            child_properties=[
                PropertySummaryResponse.from_entity(child)
                for child in prop.child_properties
                if child.deleted_at is None
            ],
            created_at=prop.created_at,
            updated_at=prop.updated_at,
        )
