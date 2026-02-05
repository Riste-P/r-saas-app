import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import is_superadmin
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.utils.security import hash_password
from app.database.utils.tenant import tenant_filter
from app.database.models.user import User
from app.dto.user import CreateUserRequest, UpdateUserRequest

logger = logging.getLogger(__name__)


async def list_users(
    current_user: User, db: AsyncSession, *, offset: int = 0, limit: int = 50
) -> tuple[list[User], int]:
    """Return (users, total_count) with pagination. Excludes soft-deleted users."""
    base = select(User).options(selectinload(User.role), selectinload(User.tenant))
    base = base.where(User.deleted_at.is_(None))
    base = tenant_filter(base, current_user, User.tenant_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(User.created_at).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_user(body: CreateUserRequest, current_user: User, db: AsyncSession) -> User:
    existing = await db.execute(
        select(User).where(User.email == body.email, User.deleted_at.is_(None))
    )
    if existing.scalar_one_or_none():
        raise ConflictError("EMAIL_EXISTS", "Email already exists")

    target_tenant_id = current_user.tenant_id
    if body.tenant_id is not None and is_superadmin(current_user):
        target_tenant_id = body.tenant_id

    new_user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        tenant_id=target_tenant_id,
        role_id=body.role_id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user, attribute_names=["role", "tenant"])

    logger.info("User created id=%s by=%s", new_user.id, current_user.id)
    return new_user


async def update_user(
    user_id: UUID, body: UpdateUserRequest, current_user: User, db: AsyncSession
) -> User:
    query = (
        select(User)
        .options(selectinload(User.role), selectinload(User.tenant))
        .where(User.id == user_id, User.deleted_at.is_(None))
    )
    if not is_superadmin(current_user):
        query = query.where(User.tenant_id == current_user.tenant_id)

    result = await db.execute(query)
    target = result.scalar_one_or_none()
    if not target:
        raise NotFoundError("USER_NOT_FOUND", "User not found")

    if target.role.name == "superadmin":
        raise ForbiddenError("SUPERADMIN_PROTECTED", "Cannot modify superadmin account")

    if body.role_id is not None:
        target.role_id = body.role_id
    if body.is_active is not None:
        target.is_active = body.is_active

    await db.commit()
    await db.refresh(target, attribute_names=["role", "tenant"])

    logger.info("User updated id=%s by=%s", user_id, current_user.id)
    return target


async def delete_user(user_id: UUID, current_user: User, db: AsyncSession) -> None:
    """Soft-delete a user by setting deleted_at timestamp."""
    query = (
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id, User.deleted_at.is_(None))
    )
    if not is_superadmin(current_user):
        query = query.where(User.tenant_id == current_user.tenant_id)

    result = await db.execute(query)
    target = result.scalar_one_or_none()
    if not target:
        raise NotFoundError("USER_NOT_FOUND", "User not found")

    if target.role.name == "superadmin":
        raise ForbiddenError("SUPERADMIN_PROTECTED", "Cannot delete superadmin account")

    target.deleted_at = datetime.now(timezone.utc)
    target.is_active = False
    await db.commit()
    logger.info("User soft-deleted id=%s by=%s", user_id, current_user.id)
