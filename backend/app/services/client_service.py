import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.database.models.client import Client
from app.database.models.property import Property
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.client import CreateClientRequest, UpdateClientRequest

logger = logging.getLogger(__name__)


async def list_clients(
    current_user: User, db: AsyncSession, *, offset: int = 0, limit: int = 50
) -> tuple[list[tuple[Client, int]], int]:
    base = (
        select(Client)
        .where(Client.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, Client.tenant_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    # Subquery for property count
    prop_count = (
        select(func.count(Property.id))
        .where(
            Property.client_id == Client.id,
            Property.deleted_at.is_(None),
        )
        .correlate(Client)
        .scalar_subquery()
    )

    query = (
        select(Client, prop_count.label("property_count"))
        .where(Client.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Client.tenant_id)
    query = query.order_by(Client.created_at).offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()
    return [(row[0], row[1]) for row in rows], total


async def get_client(
    client_id: UUID, current_user: User, db: AsyncSession
) -> Client:
    query = (
        select(Client)
        .where(Client.id == client_id, Client.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Client.tenant_id)

    result = await db.execute(query)
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundError("CLIENT_NOT_FOUND", "Client not found")
    return client


async def create_client(
    body: CreateClientRequest, current_user: User, db: AsyncSession
) -> Client:
    existing = await db.execute(
        select(Client).where(
            Client.name == body.name,
            Client.tenant_id == current_user.tenant_id,
            Client.deleted_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("NAME_EXISTS", "A client with this name already exists")

    client = Client(
        name=body.name,
        email=body.email,
        phone=body.phone,
        address=body.address,
        billing_address=body.billing_address,
        notes=body.notes,
        tenant_id=current_user.tenant_id,
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)

    logger.info("Client created id=%s by=%s", client.id, current_user.id)
    return client


async def update_client(
    client_id: UUID,
    body: UpdateClientRequest,
    current_user: User,
    db: AsyncSession,
) -> Client:
    client = await get_client(client_id, current_user, db)

    if body.name is not None and body.name != client.name:
        existing = await db.execute(
            select(Client).where(
                Client.name == body.name,
                Client.tenant_id == current_user.tenant_id,
                Client.deleted_at.is_(None),
                Client.id != client_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("NAME_EXISTS", "A client with this name already exists")
        client.name = body.name

    if body.email is not None:
        client.email = body.email
    if body.phone is not None:
        client.phone = body.phone
    if body.address is not None:
        client.address = body.address
    if body.billing_address is not None:
        client.billing_address = body.billing_address
    if body.notes is not None:
        client.notes = body.notes
    if body.is_active is not None:
        client.is_active = body.is_active

    client.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(client)

    logger.info("Client updated id=%s by=%s", client_id, current_user.id)
    return client


async def delete_client(
    client_id: UUID, current_user: User, db: AsyncSession
) -> None:
    client = await get_client(client_id, current_user, db)

    now = datetime.now(timezone.utc)
    client.deleted_at = now
    client.updated_at = now
    client.is_active = False

    # Also soft-delete associated properties
    props_result = await db.execute(
        select(Property).where(
            Property.client_id == client_id,
            Property.deleted_at.is_(None),
        )
    )
    for prop in props_result.scalars().all():
        prop.deleted_at = now
        prop.updated_at = now
        prop.is_active = False

    await db.commit()
    logger.info("Client soft-deleted id=%s by=%s", client_id, current_user.id)
