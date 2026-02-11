from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

from app.database.models.property import PropertyType

if TYPE_CHECKING:
    from app.database.models.property import Property


class CreatePropertyRequest(BaseModel):
    client_id: UUID | None = None
    parent_property_id: UUID | None = None
    property_type: PropertyType
    name: str
    address: str | None = None
    city: str | None = None
    notes: str | None = None


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
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, prop: Property) -> PropertyResponse:
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
                PropertySummaryResponse.from_entity(child)
                for child in prop.child_properties
                if child.deleted_at is None
            ],
            created_at=prop.created_at,
            updated_at=prop.updated_at,
        )
