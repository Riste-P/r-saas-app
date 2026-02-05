import os
import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base, get_db
from app.utils.security import hash_password
from app.main import app
from app.database.models.role import Role
from app.database.models.tenant import Tenant
from app.database.models.user import User

_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
_DB_USER = os.getenv("TEST_DB_USER", "saas")
_DB_PASS = os.getenv("TEST_DB_PASS", "saas_dev_password_2026")

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/saas_test"
)
_ROOT_URL = f"postgresql+asyncpg://{_DB_USER}:{_DB_PASS}@{_DB_HOST}:{_DB_PORT}/saas_db"


@pytest_asyncio.fixture(autouse=True)
async def _test_db():
    """Create the test DB if needed, create all tables, yield session factory, then drop everything."""
    # Ensure the test database exists
    root_engine = create_async_engine(_ROOT_URL, isolation_level="AUTOCOMMIT")
    async with root_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'saas_test'")
        )
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE saas_test"))
    await root_engine.dispose()

    # Create tables
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Override the app's get_db dependency
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Store on module-level so other fixtures can access it
    _state["session_factory"] = session_factory

    yield

    # Drop all tables and dispose
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    app.dependency_overrides.pop(get_db, None)


# Shared state dict for passing data between fixtures
_state: dict = {}


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with _state["session_factory"]() as session:
        yield session


@pytest_asyncio.fixture
async def seed(db: AsyncSession):
    """Seed roles, system tenant, and a superadmin user."""
    role_superadmin = Role(id=1, name="superadmin")
    role_admin = Role(id=2, name="admin")
    role_user = Role(id=3, name="user")
    db.add_all([role_superadmin, role_admin, role_user])

    system_tenant = Tenant(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        name="System",
        slug="system",
    )
    db.add(system_tenant)
    await db.flush()

    superadmin = User(
        email="admin@system.com",
        hashed_password=hash_password("admin123"),
        tenant_id=system_tenant.id,
        role_id=1,
    )
    db.add(superadmin)
    await db.commit()

    return {"superadmin": superadmin, "system_tenant": system_tenant}


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, seed) -> AsyncClient:
    """Client with superadmin auth token."""
    resp = await client.post(
        "/api/auth/login",
        json={"email": "admin@system.com", "password": "admin123"},
    )
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
