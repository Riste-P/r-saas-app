"""add invoices and payments

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-21 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Invoices
    op.create_table('invoices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('draft', 'sent', 'paid', 'overdue', 'cancelled', name='invoice_status_enum'), nullable=False, server_default='draft'),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('discount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('tax', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoices_property_id'), 'invoices', ['property_id'], unique=False)
    op.create_index(op.f('ix_invoices_tenant_id'), 'invoices', ['tenant_id'], unique=False)
    op.create_index(
        'uq_invoice_number_per_tenant',
        'invoices',
        ['tenant_id', 'invoice_number'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )

    # Invoice items
    op.create_table('invoice_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('service_type_id', sa.UUID(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=8, scale=2), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.ForeignKeyConstraint(['service_type_id'], ['service_types.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invoice_items_invoice_id'), 'invoice_items', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_invoice_items_tenant_id'), 'invoice_items', ['tenant_id'], unique=False)

    # Payments
    op.create_table('payments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('invoice_id', sa.UUID(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.Enum('cash', 'bank_transfer', 'card', 'other', name='payment_method_enum'), nullable=False),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_invoice_id'), 'payments', ['invoice_id'], unique=False)
    op.create_index(op.f('ix_payments_tenant_id'), 'payments', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_payments_tenant_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_invoice_id'), table_name='payments')
    op.drop_table('payments')

    op.drop_index(op.f('ix_invoice_items_tenant_id'), table_name='invoice_items')
    op.drop_index(op.f('ix_invoice_items_invoice_id'), table_name='invoice_items')
    op.drop_table('invoice_items')

    op.drop_index('uq_invoice_number_per_tenant', table_name='invoices')
    op.drop_index(op.f('ix_invoices_tenant_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_property_id'), table_name='invoices')
    op.drop_table('invoices')

    sa.Enum(name='payment_method_enum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='invoice_status_enum').drop(op.get_bind(), checkfirst=True)
