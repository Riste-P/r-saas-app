from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import require_role
from app.core.pagination import PaginationParams
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.tenant import CreateTenantRequest, TenantResponse, UpdateTenantRequest
from app.services import tenant_service

router = APIRouter(prefix="/admin/tenants", tags=["tenants"])


@router.get("", response_model=PaginatedResponse[TenantResponse])
async def list_tenants(
    pagination: PaginationParams = Depends(),
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    tenants, total = await tenant_service.list_tenants(
        db, offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[TenantResponse.from_entity(t) for t in tenants],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: CreateTenantRequest,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await tenant_service.create_tenant(body, db)
    return TenantResponse.from_entity(tenant)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    body: UpdateTenantRequest,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    tenant = await tenant_service.update_tenant(tenant_id, body, db)
    return TenantResponse.from_entity(tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await tenant_service.delete_tenant(tenant_id, db)
