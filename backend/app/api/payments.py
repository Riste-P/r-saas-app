from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.core.pagination import PaginationParams
from app.database import get_db
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    UpdatePaymentRequest,
)
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=PaginatedResponse[PaymentResponse])
async def list_payments(
    pagination: PaginationParams = Depends(),
    invoice_id: UUID | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await payment_service.list_payments(
        user,
        db,
        offset=pagination.offset,
        limit=pagination.limit,
        invoice_id=invoice_id,
    )
    return PaginatedResponse(
        items=[PaymentResponse.from_entity(p) for p in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    body: CreatePaymentRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    p = await payment_service.create_payment(body, user, db)
    return PaymentResponse.from_entity(p)


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    body: UpdatePaymentRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    p = await payment_service.update_payment(payment_id, body, user, db)
    return PaymentResponse.from_entity(p)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await payment_service.delete_payment(payment_id, user, db)
