import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.database.models.invoice import Invoice, InvoiceStatus
from app.database.models.payment import Payment, PaymentMethod
from app.database.models.user import User
from app.database.utils.common import tenant_filter
from app.dto.payment import CreatePaymentRequest, UpdatePaymentRequest

logger = logging.getLogger(__name__)


async def _get_payment(
    payment_id: UUID, current_user: User, db: AsyncSession
) -> Payment:
    query = (
        select(Payment)
        .options(selectinload(Payment.invoice))
        .where(Payment.id == payment_id, Payment.deleted_at.is_(None))
    )
    query = tenant_filter(query, current_user, Payment.tenant_id)
    result = await db.execute(query)
    p = result.scalar_one_or_none()
    if not p:
        raise NotFoundError("PAYMENT_NOT_FOUND", "Payment not found")
    return p


async def _total_payments_for_invoice(
    invoice_id: UUID, db: AsyncSession
) -> Decimal:
    result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), Decimal("0"))).where(
            Payment.invoice_id == invoice_id,
            Payment.deleted_at.is_(None),
        )
    )
    return result.scalar_one()


async def _update_invoice_paid_status(
    invoice: Invoice, db: AsyncSession
) -> None:
    """Auto-set or revert paid status based on total payments."""
    total_paid = await _total_payments_for_invoice(invoice.id, db)
    if total_paid >= invoice.total and invoice.status != InvoiceStatus.paid:
        invoice.status = InvoiceStatus.paid
        invoice.paid_date = date.today()
        invoice.updated_at = datetime.now(timezone.utc)
    elif total_paid < invoice.total and invoice.status == InvoiceStatus.paid:
        invoice.status = InvoiceStatus.sent
        invoice.paid_date = None
        invoice.updated_at = datetime.now(timezone.utc)


async def list_payments(
    current_user: User,
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 50,
    invoice_id: UUID | None = None,
) -> tuple[list[Payment], int]:
    base = (
        select(Payment)
        .options(selectinload(Payment.invoice))
        .where(Payment.deleted_at.is_(None))
    )
    base = tenant_filter(base, current_user, Payment.tenant_id)

    if invoice_id is not None:
        base = base.where(Payment.invoice_id == invoice_id)

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    query = base.order_by(Payment.payment_date.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def create_payment(
    body: CreatePaymentRequest, current_user: User, db: AsyncSession
) -> Payment:
    # Validate invoice belongs to tenant
    inv_q = select(Invoice).where(
        Invoice.id == body.invoice_id, Invoice.deleted_at.is_(None)
    )
    inv_q = tenant_filter(inv_q, current_user, Invoice.tenant_id)
    inv_result = await db.execute(inv_q)
    invoice = inv_result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("INVOICE_NOT_FOUND", "Invoice not found")

    payment = Payment(
        invoice_id=body.invoice_id,
        amount=body.amount,
        payment_date=body.payment_date,
        payment_method=PaymentMethod(body.payment_method),
        reference=body.reference,
        notes=body.notes,
        tenant_id=current_user.tenant_id,
    )
    db.add(payment)
    await db.flush()

    # Check if invoice is now fully paid
    await _update_invoice_paid_status(invoice, db)

    await db.commit()

    # Reload with invoice relationship
    return await _get_payment(payment.id, current_user, db)


async def update_payment(
    payment_id: UUID,
    body: UpdatePaymentRequest,
    current_user: User,
    db: AsyncSession,
) -> Payment:
    payment = await _get_payment(payment_id, current_user, db)

    if body.amount is not None:
        payment.amount = body.amount
    if body.payment_date is not None:
        payment.payment_date = body.payment_date
    if body.payment_method is not None:
        payment.payment_method = PaymentMethod(body.payment_method)
    if body.reference is not None:
        payment.reference = body.reference
    if body.notes is not None:
        payment.notes = body.notes

    payment.updated_at = datetime.now(timezone.utc)

    # Re-check paid status
    invoice = payment.invoice
    await _update_invoice_paid_status(invoice, db)

    await db.commit()
    logger.info("Payment updated id=%s by=%s", payment_id, current_user.id)
    return await _get_payment(payment_id, current_user, db)


async def delete_payment(
    payment_id: UUID, current_user: User, db: AsyncSession
) -> None:
    payment = await _get_payment(payment_id, current_user, db)
    invoice = payment.invoice

    now = datetime.now(timezone.utc)
    payment.deleted_at = now
    payment.updated_at = now

    # Revert invoice paid status if needed
    await _update_invoice_paid_status(invoice, db)

    await db.commit()
    logger.info("Payment soft-deleted id=%s by=%s", payment_id, current_user.id)
