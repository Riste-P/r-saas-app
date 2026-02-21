from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.property_service_type import PropertyServiceType


class AssignServiceRequest(BaseModel):
    property_id: UUID
    service_type_id: UUID
    custom_price: Decimal | None = None
    is_active: bool = True


class BulkAssignServicesRequest(BaseModel):
    property_id: UUID
    service_type_ids: list[UUID]


class UpdatePropertyServiceRequest(BaseModel):
    custom_price: Decimal | None = None
    is_active: bool | None = None


class PropertyServiceTypeResponse(BaseModel):
    id: UUID
    property_id: UUID
    service_type_id: UUID
    service_type_name: str
    custom_price: Decimal | None
    effective_price: Decimal
    is_active: bool
    is_inherited: bool
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(
        cls,
        pst: PropertyServiceType,
        *,
        is_inherited: bool = False,
    ) -> PropertyServiceTypeResponse:
        effective_price = (
            pst.custom_price if pst.custom_price is not None else pst.service_type.base_price
        )
        return cls(
            id=pst.id,
            property_id=pst.property_id,
            service_type_id=pst.service_type_id,
            service_type_name=pst.service_type.name,
            custom_price=pst.custom_price,
            effective_price=effective_price,
            is_active=pst.is_active,
            is_inherited=is_inherited,
            created_at=pst.created_at,
            updated_at=pst.updated_at,
        )


class EffectiveServiceResponse(BaseModel):
    service_type_id: UUID
    service_type_name: str
    effective_price: Decimal
    is_active: bool
    is_inherited: bool
    override_id: UUID | None = None
