from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.client import Client


class CreateClientRequest(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    billing_address: str | None = None
    notes: str | None = None


class UpdateClientRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    billing_address: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    id: UUID
    name: str
    email: str | None
    phone: str | None
    address: str | None
    billing_address: str | None
    notes: str | None
    is_active: bool
    property_count: int
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, client: Client, property_count: int = 0) -> ClientResponse:
        return cls(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            address=client.address,
            billing_address=client.billing_address,
            notes=client.notes,
            is_active=client.is_active,
            property_count=property_count,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )
