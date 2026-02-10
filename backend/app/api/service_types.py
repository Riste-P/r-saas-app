from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.core.pagination import PaginationParams
from app.database import get_db
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.service_type import (
    CreateServiceTypeRequest,
    ServiceTypeResponse,
    UpdateChecklistRequest,
    UpdateServiceTypeRequest,
)
from app.services import service_type_service

router = APIRouter(prefix="/service-types", tags=["service-types"])


@router.get("", response_model=PaginatedResponse[ServiceTypeResponse])
async def list_service_types(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await service_type_service.list_service_types(
        user, db, offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[ServiceTypeResponse.from_entity(st) for st in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get("/{service_type_id}", response_model=ServiceTypeResponse)
async def get_service_type(
    service_type_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    st = await service_type_service.get_service_type(service_type_id, user, db)
    return ServiceTypeResponse.from_entity(st)


@router.post("", response_model=ServiceTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_service_type(
    body: CreateServiceTypeRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    st = await service_type_service.create_service_type(body, user, db)
    return ServiceTypeResponse.from_entity(st)


@router.patch("/{service_type_id}", response_model=ServiceTypeResponse)
async def update_service_type(
    service_type_id: UUID,
    body: UpdateServiceTypeRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    st = await service_type_service.update_service_type(service_type_id, body, user, db)
    return ServiceTypeResponse.from_entity(st)


@router.put("/{service_type_id}/checklist", response_model=ServiceTypeResponse)
async def update_checklist(
    service_type_id: UUID,
    body: UpdateChecklistRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    st = await service_type_service.update_checklist(service_type_id, body, user, db)
    return ServiceTypeResponse.from_entity(st)


@router.delete("/{service_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_type(
    service_type_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await service_type_service.delete_service_type(service_type_id, user, db)
