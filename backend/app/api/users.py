from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import require_role
from app.core.pagination import PaginationParams
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.user import CreateUserRequest, UpdateUserRequest, UserResponse
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["users"])


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    users, total = await user_service.list_users(
        user, db, offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[UserResponse.from_entity(u) for u in users],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    new_user = await user_service.create_user(body, user, db)
    return UserResponse.from_entity(new_user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    target = await user_service.update_user(user_id, body, user, db)
    return UserResponse.from_entity(target)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await user_service.delete_user(user_id, user, db)
