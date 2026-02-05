from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.pagination import PaginationParams
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
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
        items=tenants,
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    body: TenantCreate,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    return await tenant_service.create_tenant(body, db)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    body: TenantUpdate,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    return await tenant_service.update_tenant(tenant_id, body, db)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    user: User = Depends(require_role("superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await tenant_service.delete_tenant(tenant_id, db)
