import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.database.models.service_type import ChecklistItem, ServiceType
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.service_type import (
    CreateServiceTypeRequest,
    UpdateChecklistRequest,
    UpdateServiceTypeRequest,
)

logger = logging.getLogger(__name__)


async def list_service_types(
    current_user: User, db: AsyncSession, *, offset: int = 0, limit: int = 50
) -> tuple[list[ServiceType], int]:
    base = (
        select(ServiceType)
        .options(selectinload(ServiceType.checklist_items))
        .where(ServiceType.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, ServiceType.tenant_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(ServiceType.created_at).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_service_type(
    service_type_id: UUID, current_user: User, db: AsyncSession
) -> ServiceType:
    query = (
        select(ServiceType)
        .options(selectinload(ServiceType.checklist_items))
        .where(ServiceType.id == service_type_id, ServiceType.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, ServiceType.tenant_id)

    result = await db.execute(query)
    st = result.scalar_one_or_none()
    if not st:
        raise NotFoundError("SERVICE_TYPE_NOT_FOUND", "Service type not found")
    return st


async def create_service_type(
    body: CreateServiceTypeRequest, current_user: User, db: AsyncSession
) -> ServiceType:
    existing = await db.execute(
        select(ServiceType).where(
            ServiceType.name == body.name,
            ServiceType.tenant_id == current_user.tenant_id,
            ServiceType.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("NAME_EXISTS", "A service type with this name already exists")

    st = ServiceType(
        name=body.name,
        description=body.description,
        base_price=body.base_price,
        estimated_duration_minutes=body.estimated_duration_minutes,
        tenant_id=current_user.tenant_id,
    )
    db.add(st)
    await db.flush()

    for item in body.checklist_items:
        ci = ChecklistItem(
            service_type_id=st.id,
            name=item.name,
            description=item.description,
            sort_order=item.sort_order,
            tenant_id=current_user.tenant_id,
        )
        db.add(ci)

    await db.commit()
    await db.refresh(st, attribute_names=["checklist_items"])

    logger.info("ServiceType created id=%s by=%s", st.id, current_user.id)
    return st


async def update_service_type(
    service_type_id: UUID,
    body: UpdateServiceTypeRequest,
    current_user: User,
    db: AsyncSession,
) -> ServiceType:
    st = await get_service_type(service_type_id, current_user, db)

    if body.name is not None and body.name != st.name:
        existing = await db.execute(
            select(ServiceType).where(
                ServiceType.name == body.name,
                ServiceType.tenant_id == current_user.tenant_id,
                ServiceType.deleted_at.is_(None),
                ServiceType.id != service_type_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("NAME_EXISTS", "A service type with this name already exists")
        st.name = body.name

    if body.description is not None:
        st.description = body.description
    if body.base_price is not None:
        st.base_price = body.base_price
    if body.estimated_duration_minutes is not None:
        st.estimated_duration_minutes = body.estimated_duration_minutes
    if body.is_active is not None:
        st.is_active = body.is_active

    st.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(st, attribute_names=["checklist_items"])

    logger.info("ServiceType updated id=%s by=%s", service_type_id, current_user.id)
    return st


async def update_checklist(
    service_type_id: UUID,
    body: UpdateChecklistRequest,
    current_user: User,
    db: AsyncSession,
) -> ServiceType:
    st = await get_service_type(service_type_id, current_user, db)

    await db.execute(
        delete(ChecklistItem).where(ChecklistItem.service_type_id == st.id)
    )

    for item in body.items:
        ci = ChecklistItem(
            service_type_id=st.id,
            name=item.name,
            description=item.description,
            sort_order=item.sort_order,
            tenant_id=current_user.tenant_id,
        )
        db.add(ci)

    st.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(st, attribute_names=["checklist_items"])

    logger.info("Checklist updated for ServiceType id=%s by=%s", service_type_id, current_user.id)
    return st


async def delete_service_type(
    service_type_id: UUID, current_user: User, db: AsyncSession
) -> None:
    st = await get_service_type(service_type_id, current_user, db)

    now = datetime.now(timezone.utc)
    st.deleted_at = now
    st.updated_at = now
    st.is_active = False

    for item in st.checklist_items:
        item.deleted_at = now
        item.updated_at = now

    await db.commit()
    logger.info("ServiceType soft-deleted id=%s by=%s", service_type_id, current_user.id)
