import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email
from booking.infrastructure.persistence.repositories.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)


def make_user(email: str = "lucas@example.com") -> User:
    return User(
        id=BookingId.generate(),
        email=Email(email),
        full_name="Lucas Benítez",
        hashed_password="hashed_password",
    )


@pytest.mark.asyncio
async def test_save_and_find_user(db_session: AsyncSession) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    user = make_user()

    await repo.save(user)
    found = await repo.find_by_id(user.id)

    assert found is not None
    assert found.id == user.id
    assert str(found.email) == str(user.email)


@pytest.mark.asyncio
async def test_find_user_by_email(db_session: AsyncSession) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    user = make_user("unique@example.com")
    await repo.save(user)

    found = await repo.find_by_email(Email("unique@example.com"))

    assert found is not None
    assert found.id == user.id


@pytest.mark.asyncio
async def test_find_user_not_found(db_session: AsyncSession) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    found = await repo.find_by_id(BookingId.generate())
    assert found is None


@pytest.mark.asyncio
async def test_find_user_by_email_not_found(db_session: AsyncSession) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    found = await repo.find_by_email(Email("notexists@example.com"))
    assert found is None


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession) -> None:
    repo = SQLAlchemyUserRepository(db_session)
    user = make_user("update@example.com")
    await repo.save(user)

    user.deactivate()
    await repo.update(user)

    found = await repo.find_by_id(user.id)
    assert found is not None
    assert found.is_active is False
