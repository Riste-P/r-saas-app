import logging
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import is_superadmin
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.core.tenant import tenant_filter
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


async def list_users(
    current_user: User, db: AsyncSession, *, offset: int = 0, limit: int = 50
) -> tuple[list[User], int]:
    """Return (users, total_count) with pagination."""
    base = select(User).options(selectinload(User.role), selectinload(User.tenant))
    base = tenant_filter(base, current_user, User.tenant_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(User.created_at).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_user(body: UserCreate, current_user: User, db: AsyncSession) -> User:
    existing = await db.execute(select(User).where(User.email == body.email))
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
    user_id: UUID, body: UserUpdate, current_user: User, db: AsyncSession
) -> User:
    query = (
        select(User)
        .options(selectinload(User.role), selectinload(User.tenant))
        .where(User.id == user_id)
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


async def deactivate_user(user_id: UUID, current_user: User, db: AsyncSession) -> None:
    query = select(User).options(selectinload(User.role)).where(User.id == user_id)
    if not is_superadmin(current_user):
        query = query.where(User.tenant_id == current_user.tenant_id)

    result = await db.execute(query)
    target = result.scalar_one_or_none()
    if not target:
        raise NotFoundError("USER_NOT_FOUND", "User not found")

    if target.role.name == "superadmin":
        raise ForbiddenError("SUPERADMIN_PROTECTED", "Cannot deactivate superadmin account")

    target.is_active = False
    await db.commit()
    logger.info("User deactivated id=%s by=%s", user_id, current_user.id)
