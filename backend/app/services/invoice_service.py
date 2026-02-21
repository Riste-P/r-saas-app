import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppError, NotFoundError
from app.database.models.invoice import Invoice, InvoiceStatus
from app.database.models.invoice_item import InvoiceItem
from app.database.models.property import Property
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.invoice import (
    CreateInvoiceRequest,
    GenerateInvoicesRequest,
    UpdateInvoiceRequest,
)
from app.services import property_service_type_service

logger = logging.getLogger(__name__)


def _calc_totals(
    items: list[dict], discount: Decimal, tax: Decimal
) -> tuple[Decimal, Decimal]:
    """Return (subtotal, total) from item dicts with 'total' key."""
    subtotal = sum((i["total"] for i in items), Decimal("0"))
    total = subtotal - discount + tax
    return subtotal, total


async def _next_invoice_number(tenant_id: UUID, db: AsyncSession) -> str:
    """Generate next invoice number: INV-YYYYMM-NNNN."""
    now = datetime.now(timezone.utc)
    prefix = f"INV-{now.strftime('%Y%m')}-"

    result = await db.execute(
        select(Invoice.invoice_number)
        .where(
            Invoice.tenant_id == tenant_id,
            Invoice.invoice_number.like(f"{prefix}%"),
        )
        .order_by(Invoice.invoice_number.desc())
        .limit(1)
    )
    last = result.scalar_one_or_none()
    if last:
        seq = int(last.split("-")[-1]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


_EAGER = (
    selectinload(Invoice.property).selectinload(Property.client),
    selectinload(Invoice.items),
    selectinload(Invoice.payments),
)


async def list_invoices(
    current_user: User,
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 50,
    status: InvoiceStatus | None = None,
    property_id: UUID | None = None,
    client_id: UUID | None = None,
) -> tuple[list[Invoice], int]:
    base = (
        select(Invoice)
        .options(
            selectinload(Invoice.property).selectinload(Property.client),
        )
        .where(Invoice.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, Invoice.tenant_id)

    if status is not None:
        base = base.where(Invoice.status == status)
    if property_id is not None:
        base = base.where(Invoice.property_id == property_id)
    if client_id is not None:
        base = base.join(Invoice.property).where(Property.client_id == client_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(Invoice.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_invoice(
    invoice_id: UUID, current_user: User, db: AsyncSession
) -> Invoice:
    query = (
        select(Invoice)
        .options(*_EAGER)
        .where(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Invoice.tenant_id)

    result = await db.execute(query)
    inv = result.scalar_one_or_none()
    if not inv:
        raise NotFoundError("INVOICE_NOT_FOUND", "Invoice not found")
    return inv


async def create_invoice(
    body: CreateInvoiceRequest, current_user: User, db: AsyncSession
) -> Invoice:
    # Validate property
    prop_q = select(Property).where(
        Property.id == body.property_id, Property.deleted_at.is_(None)
    )
    prop_q = tenant_filter(prop_q, current_user, Property.tenant_id)
    prop_result = await db.execute(prop_q)
    if not prop_result.scalar_one_or_none():
        raise NotFoundError("PROPERTY_NOT_FOUND", "Property not found")

    invoice_number = await _next_invoice_number(current_user.tenant_id, db)

    # Build items
    item_dicts = []
    for i, req_item in enumerate(body.items):
        line_total = req_item.quantity * req_item.unit_price
        item_dicts.append({
            "service_type_id": req_item.service_type_id,
            "description": req_item.description,
            "quantity": req_item.quantity,
            "unit_price": req_item.unit_price,
            "total": line_total,
            "sort_order": req_item.sort_order or i,
        })

    subtotal, total = _calc_totals(item_dicts, body.discount, body.tax)

    inv = Invoice(
        property_id=body.property_id,
        invoice_number=invoice_number,
        period_start=body.period_start,
        period_end=body.period_end,
        subtotal=subtotal,
        discount=body.discount,
        tax=body.tax,
        total=total,
        issue_date=body.issue_date,
        due_date=body.due_date,
        notes=body.notes,
        tenant_id=current_user.tenant_id,
    )
    db.add(inv)
    await db.flush()

    for d in item_dicts:
        item = InvoiceItem(
            invoice_id=inv.id,
            tenant_id=current_user.tenant_id,
            **d,
        )
        db.add(item)

    await db.commit()
    logger.info("Invoice created id=%s number=%s by=%s", inv.id, invoice_number, current_user.id)
    return await get_invoice(inv.id, current_user, db)


async def update_invoice(
    invoice_id: UUID,
    body: UpdateInvoiceRequest,
    current_user: User,
    db: AsyncSession,
) -> Invoice:
    inv = await get_invoice(invoice_id, current_user, db)

    if body.status is not None:
        inv.status = InvoiceStatus(body.status)
    if body.issue_date is not None:
        inv.issue_date = body.issue_date
    if body.due_date is not None:
        inv.due_date = body.due_date
    if "paid_date" in body.model_fields_set:
        inv.paid_date = body.paid_date

    recalc = False
    if body.discount is not None:
        inv.discount = body.discount
        recalc = True
    if body.tax is not None:
        inv.tax = body.tax
        recalc = True
    if body.notes is not None:
        inv.notes = body.notes

    if recalc:
        inv.total = inv.subtotal - inv.discount + inv.tax

    inv.updated_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("Invoice updated id=%s by=%s", invoice_id, current_user.id)
    return await get_invoice(invoice_id, current_user, db)


async def generate_invoices(
    body: GenerateInvoicesRequest, current_user: User, db: AsyncSession
) -> list[Invoice]:
    """Generate invoices from effective services.

    If the property has children, create one invoice per active child.
    If no children, create one invoice for the property itself.
    """
    # Load property with children
    prop_q = (
        select(Property)
        .options(selectinload(Property.child_properties))
        .where(Property.id == body.property_id, Property.deleted_at.is_(None))
    )
    prop_q = tenant_filter(prop_q, current_user, Property.tenant_id)
    prop_result = await db.execute(prop_q)
    prop = prop_result.scalar_one_or_none()
    if not prop:
        raise NotFoundError("PROPERTY_NOT_FOUND", "Property not found")

    # Determine which properties to invoice
    active_children = [
        c for c in prop.child_properties
        if c.deleted_at is None and c.is_active
    ]
    targets = active_children if active_children else [prop]

    created_invoices: list[Invoice] = []

    for target in targets:
        # Resolve effective services for this property (filter out opted-out)
        all_effective = await property_service_type_service.get_effective_services(
            target.id, current_user, db
        )
        effective = [s for s in all_effective if s.is_active]
        if not effective:
            continue  # Skip properties with no active services

        invoice_number = await _next_invoice_number(current_user.tenant_id, db)

        # Build line items from effective services
        item_dicts = []
        for i, svc in enumerate(effective):
            line_total = svc.effective_price  # quantity=1 * unit_price
            item_dicts.append({
                "service_type_id": svc.service_type_id,
                "description": svc.service_type_name,
                "quantity": Decimal("1"),
                "unit_price": svc.effective_price,
                "total": line_total,
                "sort_order": i,
            })

        subtotal, total = _calc_totals(item_dicts, body.discount, body.tax)

        inv = Invoice(
            property_id=target.id,
            invoice_number=invoice_number,
            period_start=body.period_start,
            period_end=body.period_end,
            subtotal=subtotal,
            discount=body.discount,
            tax=body.tax,
            total=total,
            issue_date=body.issue_date,
            due_date=body.due_date,
            notes=body.notes,
            tenant_id=current_user.tenant_id,
        )
        db.add(inv)
        await db.flush()

        for d in item_dicts:
            item = InvoiceItem(
                invoice_id=inv.id,
                tenant_id=current_user.tenant_id,
                **d,
            )
            db.add(item)

        created_invoices.append(inv)

    await db.commit()

    # Reload all with relationships
    result = []
    for inv in created_invoices:
        result.append(await get_invoice(inv.id, current_user, db))

    logger.info(
        "Generated %d invoices for property=%s by=%s",
        len(result), body.property_id, current_user.id,
    )
    return result


async def mark_overdue(current_user: User, db: AsyncSession) -> int:
    """Batch mark sent invoices past due_date as overdue. Returns count updated."""
    today = date.today()
    stmt = (
        update(Invoice)
        .where(
            Invoice.status == InvoiceStatus.sent,
            Invoice.due_date < today,
            Invoice.deleted_at.is_(None),
            Invoice.tenant_id == current_user.tenant_id,
        )
        .values(status=InvoiceStatus.overdue, updated_at=datetime.now(timezone.utc))
    )
    result = await db.execute(stmt)
    await db.commit()
    count = result.rowcount
    logger.info("Marked %d invoices as overdue by=%s", count, current_user.id)
    return count


async def delete_invoice(
    invoice_id: UUID, current_user: User, db: AsyncSession
) -> None:
    inv = await get_invoice(invoice_id, current_user, db)

    if inv.status not in (InvoiceStatus.draft, InvoiceStatus.cancelled):
        raise AppError(
            "CANNOT_DELETE",
            "Only draft or cancelled invoices can be deleted",
        )

    now = datetime.now(timezone.utc)
    inv.deleted_at = now
    inv.updated_at = now

    # Soft-delete items
    for item in inv.items:
        item.deleted_at = now
        item.updated_at = now

    await db.commit()
    logger.info("Invoice soft-deleted id=%s by=%s", invoice_id, current_user.id)
