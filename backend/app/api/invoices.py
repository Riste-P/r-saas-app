from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_role
from app.core.pagination import PaginationParams
from app.database import get_db
from app.database.models.invoice import InvoiceStatus
from app.database.models.user import User
from app.dto.common import PaginatedResponse
from app.dto.invoice import (
    CreateInvoiceRequest,
    GenerateInvoicesRequest,
    InvoiceListResponse,
    InvoiceResponse,
    UpdateInvoiceRequest,
)
from app.services import invoice_service

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=PaginatedResponse[InvoiceListResponse])
async def list_invoices(
    pagination: PaginationParams = Depends(),
    status_filter: str | None = Query(None, alias="status"),
    property_id: UUID | None = Query(None),
    client_id: UUID | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inv_status = InvoiceStatus(status_filter) if status_filter else None
    items, total = await invoice_service.list_invoices(
        user,
        db,
        offset=pagination.offset,
        limit=pagination.limit,
        status=inv_status,
        property_id=property_id,
        client_id=client_id,
    )
    return PaginatedResponse(
        items=[InvoiceListResponse.from_entity(inv) for inv in items],
        total=total,
        offset=pagination.offset,
        limit=pagination.limit,
    )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    inv = await invoice_service.get_invoice(invoice_id, user, db)
    return InvoiceResponse.from_entity(inv)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    body: CreateInvoiceRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    inv = await invoice_service.create_invoice(body, user, db)
    return InvoiceResponse.from_entity(inv)


@router.post("/generate", response_model=list[InvoiceResponse], status_code=status.HTTP_201_CREATED)
async def generate_invoices(
    body: GenerateInvoicesRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    invoices = await invoice_service.generate_invoices(body, user, db)
    return [InvoiceResponse.from_entity(inv) for inv in invoices]


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: UUID,
    body: UpdateInvoiceRequest,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    inv = await invoice_service.update_invoice(invoice_id, body, user, db)
    return InvoiceResponse.from_entity(inv)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: UUID,
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    await invoice_service.delete_invoice(invoice_id, user, db)


@router.post("/mark-overdue")
async def mark_overdue(
    user: User = Depends(require_role("admin", "superadmin")),
    db: AsyncSession = Depends(get_db),
):
    count = await invoice_service.mark_overdue(user, db)
    return {"marked_overdue": count}
