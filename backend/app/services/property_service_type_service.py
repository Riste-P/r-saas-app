import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.database.models.property import Property
from app.database.models.property_service_type import PropertyServiceType
from app.database.models.service_type import ServiceType
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.property_service_type import (
    AssignServiceRequest,
    BulkAssignServicesRequest,
    EffectiveServiceResponse,
    UpdatePropertyServiceRequest,
)

logger = logging.getLogger(__name__)


async def _get_property(
    property_id: UUID, current_user: User, db: AsyncSession
) -> Property:
    query = (
        select(Property)
        .where(Property.id == property_id, Property.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Property.tenant_id)
    result = await db.execute(query)
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundError("PROPERTY_NOT_FOUND", "Property not found")
    return prop


async def _get_assignments(
    property_id: UUID, current_user: User, db: AsyncSession
) -> list[PropertyServiceType]:
    query = (
        select(PropertyServiceType)
        .options(selectinload(PropertyServiceType.service_type))
        .where(
            PropertyServiceType.property_id == property_id,
            PropertyServiceType.deleted_at.is_(None),
        )
    )
    query = tenant_filter(query, current_user, PropertyServiceType.tenant_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def list_assignments(
    property_id: UUID, current_user: User, db: AsyncSession
) -> list[PropertyServiceType]:
    await _get_property(property_id, current_user, db)
    return await _get_assignments(property_id, current_user, db)


async def get_effective_services(
    property_id: UUID, current_user: User, db: AsyncSession
) -> list[EffectiveServiceResponse]:
    prop = await _get_property(property_id, current_user, db)

    # Get direct assignments for this property
    direct = await _get_assignments(property_id, current_user, db)
    direct_by_st = {a.service_type_id: a for a in direct}

    # Get parent assignments if property has a parent
    parent_assignments: list[PropertyServiceType] = []
    if prop.parent_property_id is not None:
        parent_assignments = await _get_assignments(
            prop.parent_property_id, current_user, db
        )

    effective: list[EffectiveServiceResponse] = []

    # Process parent services first (inherited)
    for pa in parent_assignments:
        if not pa.is_active:
            continue  # Parent deactivated this service entirely
        if pa.service_type_id in direct_by_st:
            # Child has an override for this service
            override = direct_by_st[pa.service_type_id]
            eff_price = (
                override.custom_price
                if override.custom_price is not None
                else pa.custom_price
                if pa.custom_price is not None
                else pa.service_type.base_price
            )
            effective.append(
                EffectiveServiceResponse(
                    service_type_id=pa.service_type_id,
                    service_type_name=pa.service_type.name,
                    effective_price=eff_price,
                    is_active=override.is_active,
                    is_inherited=True,
                    override_id=override.id,
                )
            )
        else:
            # Inherited as-is from parent
            eff_price = (
                pa.custom_price
                if pa.custom_price is not None
                else pa.service_type.base_price
            )
            effective.append(
                EffectiveServiceResponse(
                    service_type_id=pa.service_type_id,
                    service_type_name=pa.service_type.name,
                    effective_price=eff_price,
                    is_active=True,
                    is_inherited=True,
                    override_id=None,
                )
            )

    # Add direct-only services (not inherited from parent)
    parent_st_ids = {pa.service_type_id for pa in parent_assignments}
    for da in direct:
        if da.service_type_id not in parent_st_ids:
            eff_price = (
                da.custom_price
                if da.custom_price is not None
                else da.service_type.base_price
            )
            effective.append(
                EffectiveServiceResponse(
                    service_type_id=da.service_type_id,
                    service_type_name=da.service_type.name,
                    effective_price=eff_price,
                    is_active=da.is_active,
                    is_inherited=False,
                    override_id=da.id,
                )
            )

    return effective


async def assign_service(
    body: AssignServiceRequest, current_user: User, db: AsyncSession
) -> PropertyServiceType:
    await _get_property(body.property_id, current_user, db)

    # Validate service type belongs to tenant
    st_query = select(ServiceType).where(
        ServiceType.id == body.service_type_id,
        ServiceType.deleted_at.is_(None),
    )
    st_query = tenant_filter(st_query, current_user, ServiceType.tenant_id)
    st_result = await db.execute(st_query)
    if not st_result.scalar_one_or_none():
        raise NotFoundError("SERVICE_TYPE_NOT_FOUND", "Service type not found")

    # Check for existing assignment
    existing_query = select(PropertyServiceType).where(
        PropertyServiceType.property_id == body.property_id,
        PropertyServiceType.service_type_id == body.service_type_id,
        PropertyServiceType.deleted_at.is_(None),
    )
    existing_query = tenant_filter(
        existing_query, current_user, PropertyServiceType.tenant_id
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise ConflictError(
            "ALREADY_ASSIGNED",
            "This service is already assigned to this property",
        )

    pst = PropertyServiceType(
        property_id=body.property_id,
        service_type_id=body.service_type_id,
        custom_price=body.custom_price,
        is_active=body.is_active,
        tenant_id=current_user.tenant_id,
    )
    db.add(pst)
    await db.commit()

    # Reload with service_type relationship
    query = (
        select(PropertyServiceType)
        .options(selectinload(PropertyServiceType.service_type))
        .where(PropertyServiceType.id == pst.id)
    )
    result = await db.execute(query)
    pst = result.scalar_one()

    logger.info(
        "Service assigned property=%s service_type=%s by=%s",
        body.property_id,
        body.service_type_id,
        current_user.id,
    )
    return pst


async def bulk_assign_services(
    body: BulkAssignServicesRequest, current_user: User, db: AsyncSession
) -> list[PropertyServiceType]:
    await _get_property(body.property_id, current_user, db)

    # Validate all service types belong to tenant
    st_query = (
        select(ServiceType)
        .where(
            ServiceType.id.in_(body.service_type_ids),
            ServiceType.deleted_at.is_(None),
        )
    )
    st_query = tenant_filter(st_query, current_user, ServiceType.tenant_id)
    st_result = await db.execute(st_query)
    found_ids = {st.id for st in st_result.scalars().all()}
    missing = set(body.service_type_ids) - found_ids
    if missing:
        raise NotFoundError("SERVICE_TYPE_NOT_FOUND", "Some service types not found")

    # Get existing assignments
    existing_query = select(PropertyServiceType).where(
        PropertyServiceType.property_id == body.property_id,
        PropertyServiceType.service_type_id.in_(body.service_type_ids),
        PropertyServiceType.deleted_at.is_(None),
    )
    existing_query = tenant_filter(
        existing_query, current_user, PropertyServiceType.tenant_id
    )
    existing_result = await db.execute(existing_query)
    existing_ids = {pst.service_type_id for pst in existing_result.scalars().all()}

    created = []
    for st_id in body.service_type_ids:
        if st_id in existing_ids:
            continue  # Skip already assigned
        pst = PropertyServiceType(
            property_id=body.property_id,
            service_type_id=st_id,
            tenant_id=current_user.tenant_id,
        )
        db.add(pst)
        created.append(pst)

    await db.commit()

    # Reload all with service_type relationship
    return await _get_assignments(body.property_id, current_user, db)


async def update_assignment(
    assignment_id: UUID,
    body: UpdatePropertyServiceRequest,
    current_user: User,
    db: AsyncSession,
) -> PropertyServiceType:
    query = (
        select(PropertyServiceType)
        .options(selectinload(PropertyServiceType.service_type))
        .where(
            PropertyServiceType.id == assignment_id,
            PropertyServiceType.deleted_at.is_(None),
        )
    )
    query = tenant_filter(query, current_user, PropertyServiceType.tenant_id)
    result = await db.execute(query)
    pst = result.scalar_one_or_none()
    if not pst:
        raise NotFoundError("ASSIGNMENT_NOT_FOUND", "Service assignment not found")

    if "custom_price" in body.model_fields_set:
        pst.custom_price = body.custom_price
    if body.is_active is not None:
        pst.is_active = body.is_active

    pst.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(pst, attribute_names=["service_type"])

    logger.info("Assignment updated id=%s by=%s", assignment_id, current_user.id)
    return pst


async def remove_assignment(
    assignment_id: UUID, current_user: User, db: AsyncSession
) -> None:
    query = (
        select(PropertyServiceType)
        .options(selectinload(PropertyServiceType.property))
        .where(
            PropertyServiceType.id == assignment_id,
            PropertyServiceType.deleted_at.is_(None),
        )
    )
    query = tenant_filter(query, current_user, PropertyServiceType.tenant_id)
    result = await db.execute(query)
    pst = result.scalar_one_or_none()
    if not pst:
        raise NotFoundError("ASSIGNMENT_NOT_FOUND", "Service assignment not found")

    is_override = pst.property.parent_property_id is not None

    if is_override:
        # Hard delete overrides — they're lightweight and can be recreated
        await db.delete(pst)
    else:
        # Soft delete direct assignments on parents
        now = datetime.now(timezone.utc)
        pst.deleted_at = now
        pst.updated_at = now

    await db.commit()
    logger.info("Assignment removed id=%s override=%s by=%s", assignment_id, is_override, current_user.id)
