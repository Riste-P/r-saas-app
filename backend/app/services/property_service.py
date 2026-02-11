import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.database.models.client import Client
from app.database.models.property import Property, PropertyType
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
) -> tuple[list[Property], int]:
    base = (
        select(Property)
        .options(selectinload(Property.client), selectinload(Property.child_properties))
        .where(Property.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, Property.tenant_id)

    if client_id is not None:
        base = base.where(Property.client_id == client_id)
    if property_type is not None:
        base = base.where(Property.property_type == property_type)
    if parent_property_id is not None:
        base = base.where(Property.parent_property_id == parent_property_id)

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
        .options(selectinload(Property.client), selectinload(Property.child_properties))
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
    # Validate client belongs to tenant
    client_query = select(Client).where(
        Client.id == body.client_id,
        Client.deleted_at.is_(None),
    )
    client_query = tenant_filter(client_query, current_user, Client.tenant_id)
    client_result = await db.execute(client_query)
    if not client_result.scalar_one_or_none():
        raise NotFoundError("CLIENT_NOT_FOUND", "Client not found")

    # Validate parent property if provided
    if body.parent_property_id is not None:
        parent_query = select(Property).where(
            Property.id == body.parent_property_id,
            Property.deleted_at.is_(None),
            Property.property_type == PropertyType.building,
        )
        parent_query = tenant_filter(parent_query, current_user, Property.tenant_id)
        parent_result = await db.execute(parent_query)
        if not parent_result.scalar_one_or_none():
            raise NotFoundError(
                "PARENT_NOT_FOUND",
                "Parent property not found or is not a building",
            )

    prop = Property(
        client_id=body.client_id,
        parent_property_id=body.parent_property_id,
        property_type=body.property_type,
        name=body.name,
        address=body.address,
        city=body.city,
        postal_code=body.postal_code,
        size_sqm=body.size_sqm,
        num_rooms=body.num_rooms,
        floor=body.floor,
        access_instructions=body.access_instructions,
        key_code=body.key_code,
        contact_name=body.contact_name,
        contact_phone=body.contact_phone,
        contact_email=body.contact_email,
        tenant_id=current_user.tenant_id,
    )
    db.add(prop)
    await db.commit()
    await db.refresh(prop, attribute_names=["client", "child_properties"])

    logger.info("Property created id=%s by=%s", prop.id, current_user.id)
    return prop


async def update_property(
    property_id: UUID,
    body: UpdatePropertyRequest,
    current_user: User,
    db: AsyncSession,
) -> Property:
    prop = await get_property(property_id, current_user, db)

    if body.client_id is not None and body.client_id != prop.client_id:
        client_query = select(Client).where(
            Client.id == body.client_id,
            Client.deleted_at.is_(None),
        )
        client_query = tenant_filter(client_query, current_user, Client.tenant_id)
        client_result = await db.execute(client_query)
        if not client_result.scalar_one_or_none():
            raise NotFoundError("CLIENT_NOT_FOUND", "Client not found")
        prop.client_id = body.client_id

    if body.parent_property_id is not None:
        if body.parent_property_id != prop.parent_property_id:
            parent_query = select(Property).where(
                Property.id == body.parent_property_id,
                Property.deleted_at.is_(None),
                Property.property_type == PropertyType.building,
            )
            parent_query = tenant_filter(parent_query, current_user, Property.tenant_id)
            parent_result = await db.execute(parent_query)
            if not parent_result.scalar_one_or_none():
                raise NotFoundError(
                    "PARENT_NOT_FOUND",
                    "Parent property not found or is not a building",
                )
            prop.parent_property_id = body.parent_property_id

    if body.property_type is not None:
        prop.property_type = body.property_type
    if body.name is not None:
        prop.name = body.name
    if body.address is not None:
        prop.address = body.address
    if body.city is not None:
        prop.city = body.city
    if body.postal_code is not None:
        prop.postal_code = body.postal_code
    if body.size_sqm is not None:
        prop.size_sqm = body.size_sqm
    if body.num_rooms is not None:
        prop.num_rooms = body.num_rooms
    if body.floor is not None:
        prop.floor = body.floor
    if body.access_instructions is not None:
        prop.access_instructions = body.access_instructions
    if body.key_code is not None:
        prop.key_code = body.key_code
    if body.contact_name is not None:
        prop.contact_name = body.contact_name
    if body.contact_phone is not None:
        prop.contact_phone = body.contact_phone
    if body.contact_email is not None:
        prop.contact_email = body.contact_email
    if body.is_active is not None:
        prop.is_active = body.is_active

    prop.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(prop, attribute_names=["client", "child_properties"])

    logger.info("Property updated id=%s by=%s", property_id, current_user.id)
    return prop


async def delete_property(
    property_id: UUID, current_user: User, db: AsyncSession
) -> None:
    prop = await get_property(property_id, current_user, db)

    now = datetime.now(timezone.utc)
    prop.deleted_at = now
    prop.updated_at = now
    prop.is_active = False

    # Also soft-delete child properties (apartments in a building)
    for child in prop.child_properties:
        if child.deleted_at is None:
            child.deleted_at = now
            child.updated_at = now
            child.is_active = False

    await db.commit()
    logger.info("Property soft-deleted id=%s by=%s", property_id, current_user.id)
