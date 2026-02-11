from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.core.pagination import PaginationParams
from app.database import get_db
from app.database.models.user import User
from app.dto.client import ClientResponse, CreateClientRequest, UpdateClientRequest
from app.dto.common import PaginatedResponse
from app.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    pagination: PaginationParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows, total = await client_service.list_clients(
        user, db, offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[ClientResponse.from_entity(client, prop_count) for client, prop_count in rows],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.get_client(client_id, user, db)
    return ClientResponse.from_entity(client)


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    body: CreateClientRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.create_client(body, user, db)
    return ClientResponse.from_entity(client)


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    body: UpdateClientRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    client = await client_service.update_client(client_id, body, user, db)
    return ClientResponse.from_entity(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await client_service.delete_client(client_id, user, db)
