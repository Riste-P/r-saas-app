from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.tenant import Tenant


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class UpdateTenantRequest(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, tenant: Tenant) -> TenantResponse:
        return cls(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            is_active=tenant.is_active,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
