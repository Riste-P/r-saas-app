from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    access, refresh = await auth_service.authenticate(body.email, body.password, db)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    access = await auth_service.refresh_access_token(body.refresh_token, db)
    return AccessTokenResponse(access_token=access)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        tenant_name=user.tenant.name,
        role=user.role.name,
    )
