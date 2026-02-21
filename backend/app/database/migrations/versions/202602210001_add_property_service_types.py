"""add property service types

Revision ID: a1b2c3d4e5f6
Revises: 416468d98772
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '416468d98772'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('property_service_types',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('property_id', sa.UUID(), nullable=False),
        sa.Column('service_type_id', sa.UUID(), nullable=False),
        sa.Column('custom_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id']),
        sa.ForeignKeyConstraint(['service_type_id'], ['service_types.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_property_service_types_property_id'), 'property_service_types', ['property_id'], unique=False)
    op.create_index(op.f('ix_property_service_types_service_type_id'), 'property_service_types', ['service_type_id'], unique=False)
    op.create_index(op.f('ix_property_service_types_tenant_id'), 'property_service_types', ['tenant_id'], unique=False)
    op.create_index(
        'uq_property_service_type_active',
        'property_service_types',
        ['property_id', 'service_type_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_property_service_type_active', table_name='property_service_types')
    op.drop_index(op.f('ix_property_service_types_tenant_id'), table_name='property_service_types')
    op.drop_index(op.f('ix_property_service_types_service_type_id'), table_name='property_service_types')
    op.drop_index(op.f('ix_property_service_types_property_id'), table_name='property_service_types')
    op.drop_table('property_service_types')
