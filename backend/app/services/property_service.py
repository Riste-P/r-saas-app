import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.database.models.client import Client
from app.database.models.property import Property, PropertyType
from app.database.models.property_service_type import PropertyServiceType
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.property import CreatePropertyRequest, UpdatePropertyRequest

logger = logging.getLogger(__name__)


async def list_properties(
    current_user: User,
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 50,
    client_id: UUID | None = None,
    property_type: PropertyType | None = None,
    parent_property_id: UUID | None = None,
    parents_only: bool = False,
) -> tuple[list[Property], int]:
    base = (
        select(Property)
        .options(
            selectinload(Property.client),
            selectinload(Property.parent_property),
            selectinload(Property.child_properties).selectinload(Property.client),
            selectinload(Property.child_properties)
                .selectinload(Property.service_assignments)
                .selectinload(PropertyServiceType.service_type),
            selectinload(Property.service_assignments)
                .selectinload(PropertyServiceType.service_type),
        )
        .where(Property.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, Property.tenant_id)

    if client_id is not None:
        base = base.where(Property.client_id == client_id)
    if property_type is not None:
        base = base.where(Property.property_type == property_type)
    if parent_property_id is not None:
        base = base.where(Property.parent_property_id == parent_property_id)
    if parents_only:
        base = base.where(Property.parent_property_id.is_(None))

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(Property.created_at).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_property(
    property_id: UUID, current_user: User, db: AsyncSession
) -> Property:
    query = (
        select(Property)
        .options(
            selectinload(Property.client),
            selectinload(Property.parent_property),
            selectinload(Property.child_properties).selectinload(Property.client),
            selectinload(Property.child_properties)
                .selectinload(Property.service_assignments)
                .selectinload(PropertyServiceType.service_type),
            selectinload(Property.service_assignments)
                .selectinload(PropertyServiceType.service_type),
        )
        .where(Property.id == property_id, Property.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Property.tenant_id)

    result = await db.execute(query)
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundError("PROPERTY_NOT_FOUND", "Property not found")
    return prop


async def create_property(
    body: CreatePropertyRequest, current_user: User, db: AsyncSession
) -> Property:
    # Validate client belongs to tenant (if provided)
    if body.client_id is not None:
        client_query = select(Client).where(
            Client.id == body.client_id,
            Client.deleted_at.is_(None),
        )
        client_query = tenant_filter(client_query, current_user, Client.tenant_id)
        client_result = await db.execute(client_query)
        if not client_result.scalar_one_or_none():
            raise NotFoundError("CLIENT_NOT_FOUND", "Client not found")

    # Only units can be children
    if body.parent_property_id is not None and body.property_type != PropertyType.unit:
        raise AppError("INVALID_CHILD_TYPE", "Only units can be added as children of other properties")

    # Validate parent property if provided
    if body.parent_property_id is not None:
        parent_query = select(Property).where(
            Property.id == body.parent_property_id,
            Property.deleted_at.is_(None),
        )
        parent_query = tenant_filter(parent_query, current_user, Property.tenant_id)
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise NotFoundError(
                "PARENT_NOT_FOUND",
                "Parent property not found",
            )
        if parent.property_type == PropertyType.unit:
            raise AppError("INVALID_PARENT", "A unit cannot be a parent of other properties")

    if body.number_of_units and body.property_type != PropertyType.building:
        raise AppError(
            "INVALID_UNIT_COUNT",
            "Number of units can only be specified for building properties",
        )

    prop = Property(
        client_id=body.client_id,
        parent_property_id=body.parent_property_id,
        property_type=body.property_type,
        name=body.name,
        address=body.address,
        city=body.city,
        notes=body.notes,
        tenant_id=current_user.tenant_id,
    )
    db.add(prop)
    await db.flush()

    if body.number_of_units and body.property_type == PropertyType.building:
        for i in range(1, body.number_of_units + 1):
            unit = Property(
                client_id=body.client_id,
                parent_property_id=prop.id,
                property_type=PropertyType.unit,
                name=f"Unit {i}",
                address=body.address,
                city=body.city,
                notes=None,
                tenant_id=current_user.tenant_id,
            )
            db.add(unit)

    await db.commit()

    logger.info("Property created id=%s by=%s", prop.id, current_user.id)
    return await get_property(prop.id, current_user, db)


async def update_property(
    property_id: UUID,
    body: UpdatePropertyRequest,
    current_user: User,
    db: AsyncSession,
) -> Property:
    prop = await get_property(property_id, current_user, db)

    if "client_id" in body.model_fields_set:
        if body.client_id is None:
            prop.client_id = None
        elif body.client_id != prop.client_id:
            client_query = select(Client).where(
                Client.id == body.client_id,
                Client.deleted_at.is_(None),
            )
            client_query = tenant_filter(client_query, current_user, Client.tenant_id)
            client_result = await db.execute(client_query)
            if not client_result.scalar_one_or_none():
                raise NotFoundError("CLIENT_NOT_FOUND", "Client not found")
            prop.client_id = body.client_id

    if "parent_property_id" in body.model_fields_set:
        if body.parent_property_id is None:
            prop.parent_property_id = None
        elif body.parent_property_id != prop.parent_property_id:
            # Only units can be children
            effective_type = body.property_type if body.property_type is not None else prop.property_type
            if effective_type != PropertyType.unit:
                raise AppError("INVALID_CHILD_TYPE", "Only units can be added as children of other properties")
            parent_query = select(Property).where(
                Property.id == body.parent_property_id,
                Property.deleted_at.is_(None),
            )
            parent_query = tenant_filter(parent_query, current_user, Property.tenant_id)
            parent_result = await db.execute(parent_query)
            parent = parent_result.scalar_one_or_none()
            if not parent:
                raise NotFoundError(
                    "PARENT_NOT_FOUND",
                    "Parent property not found",
                )
            if parent.property_type == PropertyType.unit:
                raise AppError("INVALID_PARENT", "A unit cannot be a parent of other properties")
            prop.parent_property_id = body.parent_property_id

    if body.property_type is not None:
        prop.property_type = body.property_type
    if body.name is not None:
        prop.name = body.name
    if body.address is not None:
        prop.address = body.address
    if body.city is not None:
        prop.city = body.city
    if body.notes is not None:
        prop.notes = body.notes
    if body.is_active is not None:
        prop.is_active = body.is_active

    prop.updated_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("Property updated id=%s by=%s", property_id, current_user.id)
    return await get_property(property_id, current_user, db)


async def delete_property(
    property_id: UUID, current_user: User, db: AsyncSession
) -> None:
    prop = await get_property(property_id, current_user, db)

    now = datetime.now(timezone.utc)
    prop.deleted_at = now
    prop.updated_at = now
    prop.is_active = False

    # Also soft-delete child properties (units in a building)
    for child in prop.child_properties:
        if child.deleted_at is None:
            child.deleted_at = now
            child.updated_at = now
            child.is_active = False

    await db.commit()
    logger.info("Property soft-deleted id=%s by=%s", property_id, current_user.id)
