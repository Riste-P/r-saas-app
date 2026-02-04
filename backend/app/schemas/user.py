from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role_id: int = 3  # default to "user" role
    tenant_id: UUID | None = None  # superadmin can assign to a specific tenant


class UserUpdate(BaseModel):
    role_id: int | None = None
    is_active: bool | None = None


class UserListResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    role: str
    tenant_id: UUID
    tenant_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
