from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.database.models.service_type import ChecklistItem as ChecklistItemEntity
    from app.database.models.service_type import ServiceType


class ChecklistItemRequest(BaseModel):
    name: str
    description: str | None = None
    sort_order: int = 0


class CreateServiceTypeRequest(BaseModel):
    name: str
    description: str | None = None
    base_price: Decimal
    estimated_duration_minutes: int
    checklist_items: list[ChecklistItemRequest] = []


class UpdateServiceTypeRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    base_price: Decimal | None = None
    estimated_duration_minutes: int | None = None
    is_active: bool | None = None


class UpdateChecklistRequest(BaseModel):
    items: list[ChecklistItemRequest]


class ChecklistItemResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    sort_order: int

    @classmethod
    def from_entity(cls, item: ChecklistItemEntity) -> ChecklistItemResponse:
        return cls(
            id=item.id,
            name=item.name,
            description=item.description,
            sort_order=item.sort_order,
        )


class ServiceTypeResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    base_price: Decimal
    estimated_duration_minutes: int
    is_active: bool
    checklist_items: list[ChecklistItemResponse]
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, st: ServiceType) -> ServiceTypeResponse:
        return cls(
            id=st.id,
            name=st.name,
            description=st.description,
            base_price=st.base_price,
            estimated_duration_minutes=st.estimated_duration_minutes,
            is_active=st.is_active,
            checklist_items=[
                ChecklistItemResponse.from_entity(item)
                for item in st.checklist_items
            ],
            created_at=st.created_at,
            updated_at=st.updated_at,
        )
