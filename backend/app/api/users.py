from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.pagination import PaginationParams
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserListResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/admin/users", tags=["users"])


def _to_response(u: User) -> UserListResponse:
    return UserListResponse(
        id=u.id,
        email=u.email,
        is_active=u.is_active,
        role=u.role.name,
        tenant_id=u.tenant_id,
        tenant_name=u.tenant.name,
        created_at=u.created_at,
    )


@router.get("", response_model=PaginatedResponse[UserListResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    users, total = await user_service.list_users(
        user, db, offset=pagination.offset, limit=pagination.limit
    )
    return PaginatedResponse(
        items=[_to_response(u) for u in users],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.post("", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    new_user = await user_service.create_user(body, user, db)
    return _to_response(new_user)


@router.patch("/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    target = await user_service.update_user(user_id, body, user, db)
    return _to_response(target)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await user_service.deactivate_user(user_id, user, db)
