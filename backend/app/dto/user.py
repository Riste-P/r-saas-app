from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, EmailStr

if TYPE_CHECKING:
    from app.database.models.user import User


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role_id: int = 3  # default to "user" role
    tenant_id: UUID | None = None  # superadmin can assign to a specific tenant


class UpdateUserRequest(BaseModel):
    role_id: int | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    role: str
    tenant_id: UUID
    tenant_name: str
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            role=user.role.name,
            tenant_id=user.tenant_id,
            tenant_name=user.tenant.name,
            created_at=user.created_at,
        )
