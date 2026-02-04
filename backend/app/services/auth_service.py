import logging
from uuid import UUID

import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User

logger = logging.getLogger(__name__)


async def authenticate(email: str, password: str, db: AsyncSession) -> tuple[str, str]:
    """Validate credentials and return (access_token, refresh_token)."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant), selectinload(User.role))
        .where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Login failed for email=%s", email)
        raise UnauthorizedError("INVALID_CREDENTIALS", "Invalid credentials")

    if not user.is_active:
        raise ForbiddenError("USER_DEACTIVATED", "User is deactivated")

    if not user.tenant.is_active:
        raise ForbiddenError("TENANT_DEACTIVATED", "Tenant is deactivated")

    logger.info("Login success user=%s tenant=%s", user.id, user.tenant_id)
    return (
        create_access_token(user.id, user.tenant_id, user.role.name),
        create_refresh_token(user.id),
    )


async def refresh_access_token(refresh_token: str, db: AsyncSession) -> str:
    """Validate a refresh token and return a new access token."""
    try:
        payload = decode_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("TOKEN_EXPIRED", "Refresh token expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("INVALID_TOKEN", "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise UnauthorizedError("INVALID_TOKEN_TYPE", "Invalid token type")

    user_id = payload.get("sub")
    result = await db.execute(
        select(User)
        .options(selectinload(User.tenant), selectinload(User.role))
        .where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active or not user.tenant.is_active:
        raise UnauthorizedError("USER_INACTIVE", "User not found or inactive")

    return create_access_token(user.id, user.tenant_id, user.role.name)
