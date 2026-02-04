import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import SYSTEM_TENANT_SLUG
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate

logger = logging.getLogger(__name__)


async def list_tenants(
    db: AsyncSession, *, offset: int = 0, limit: int = 50
) -> tuple[list[Tenant], int]:
    """Return (tenants, total_count) with pagination."""
    count_result = await db.execute(select(func.count()).select_from(Tenant))
    total = count_result.scalar_one()

    query = select(Tenant).order_by(Tenant.created_at).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_tenant(body: TenantCreate, db: AsyncSession) -> Tenant:
    existing = await db.execute(select(Tenant).where(Tenant.slug == body.slug))
    if existing.scalar_one_or_none():
        raise ConflictError("SLUG_EXISTS", "Slug already exists")

    tenant = Tenant(name=body.name, slug=body.slug)
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)

    logger.info("Tenant created id=%s slug=%s", tenant.id, tenant.slug)
    return tenant


async def update_tenant(
    tenant_id: UUID, body: TenantUpdate, db: AsyncSession
) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError("TENANT_NOT_FOUND", "Tenant not found")

    if tenant.slug == SYSTEM_TENANT_SLUG:
        raise ForbiddenError("SYSTEM_TENANT_PROTECTED", "Cannot modify system tenant")

    if body.name is not None:
        tenant.name = body.name
    if body.is_active is not None:
        tenant.is_active = body.is_active

    await db.commit()
    await db.refresh(tenant)

    logger.info("Tenant updated id=%s", tenant_id)
    return tenant


async def deactivate_tenant(tenant_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise NotFoundError("TENANT_NOT_FOUND", "Tenant not found")

    if tenant.slug == SYSTEM_TENANT_SLUG:
        raise ForbiddenError("SYSTEM_TENANT_PROTECTED", "Cannot deactivate system tenant")

    tenant.is_active = False
    await db.commit()
    logger.info("Tenant deactivated id=%s", tenant_id)
