import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from booking.infrastructure.persistence.database import Base
from booking.infrastructure.persistence.models.booking_model import (
    BookingModel,  # noqa: F401
)
from booking.infrastructure.persistence.models.space_model import (
    SpaceModel,  # noqa: F401
)
from booking.infrastructure.persistence.models.user_model import UserModel  # noqa: F401

# Load project .env so DATABASE_URL is set when running pytest locally (CI sets env vars explicitly).
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://booking_test:booking_test@localhost:5433/booking_test_db",
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    # NullPool: each test gets a fresh DB connection — avoids asyncpg
    # "another operation is in progress" when the pool hands out a stale connection.
    _engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    # Outer transaction + savepoints: session joins the connection's transaction
    # (see SQLAlchemy "joining a session into an external transaction").
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
