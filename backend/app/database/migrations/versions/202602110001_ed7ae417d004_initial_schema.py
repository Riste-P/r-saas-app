"""initial schema

Revision ID: ed7ae417d004
Revises:
Create Date: 2026-02-03 17:37:43.286805

"""
import uuid
from typing import Sequence, Union

import bcrypt as _bcrypt
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ed7ae417d004"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYSTEM_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SUPERADMIN_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def upgrade() -> None:
    """Upgrade schema."""
    # --- Tables ---
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "tenants",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    # --- Seed data ---
    roles_table = sa.table("roles", sa.column("id", sa.Integer), sa.column("name", sa.String))
    tenants_table = sa.table(
        "tenants",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("slug", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    users_table = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("tenant_id", sa.UUID),
        sa.column("role_id", sa.Integer),
    )

    op.bulk_insert(roles_table, [
        {"id": 1, "name": "superadmin"},
        {"id": 2, "name": "admin"},
        {"id": 3, "name": "user"},
    ])

    op.bulk_insert(tenants_table, [
        {
            "id": SYSTEM_TENANT_ID,
            "name": "System",
            "slug": "system",
            "is_active": True,
        },
    ])

    op.bulk_insert(users_table, [
        {
            "id": SUPERADMIN_USER_ID,
            "email": "admin@system.com",
            "hashed_password": _bcrypt.hashpw(b"changeme", _bcrypt.gensalt()).decode(),
            "is_active": True,
            "tenant_id": SYSTEM_TENANT_ID,
            "role_id": 1,
        },
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("tenants")
    op.drop_table("roles")
