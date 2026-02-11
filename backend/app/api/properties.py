from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.core.pagination import PaginationParams
from app.database import get_db
from app.database.models.property import PropertyType
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.property import (
    CreatePropertyRequest,
    PropertyResponse,
    UpdatePropertyRequest,
)
from app.services import property_service

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("", response_model=PaginatedResponse[PropertyResponse])
async def list_properties(
    pagination: PaginationParams = Depends(),
    client_id: UUID | None = Query(None),
    property_type: PropertyType | None = Query(None),
    parent_property_id: UUID | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await property_service.list_properties(
        user,
        db,
        offset=pagination.offset,
        limit=pagination.limit,
        client_id=client_id,
        property_type=property_type,
        parent_property_id=parent_property_id,
    )
    return PaginatedResponse(
        items=[PropertyResponse.from_entity(prop) for prop in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prop = await property_service.get_property(property_id, user, db)
    return PropertyResponse.from_entity(prop)


@router.post("", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    body: CreatePropertyRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    prop = await property_service.create_property(body, user, db)
    return PropertyResponse.from_entity(prop)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    body: UpdatePropertyRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    prop = await property_service.update_property(property_id, body, user, db)
    return PropertyResponse.from_entity(prop)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await property_service.delete_property(property_id, user, db)
