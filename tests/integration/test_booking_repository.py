from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot
from booking.infrastructure.persistence.repositories.sqlalchemy_booking_repo import (
    SQLAlchemyBookingRepository,
)
from booking.infrastructure.persistence.repositories.sqlalchemy_space_repo import (
    SQLAlchemySpaceRepository,
)
from booking.infrastructure.persistence.repositories.sqlalchemy_user_repo import (
    SQLAlchemyUserRepository,
)

FUTURE = datetime.now(tz=UTC) + timedelta(days=30)


def make_space() -> Space:
    return Space(
        id=BookingId.generate(),
        name="Room A",
        description="Test room",
        capacity=10,
        price_per_hour=25.0,
    )


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email(f"{BookingId.generate()}@example.com"),
        full_name="Test User",
        hashed_password="hashed",
    )


def make_booking(
    space_id: BookingId, user_id: BookingId, offset_days: int = 0
) -> Booking:
    start = FUTURE + timedelta(days=offset_days)
    end = start + timedelta(hours=2)
    return Booking(
        id=BookingId.generate(),
        space_id=space_id,
        user_id=user_id,
        time_slot=TimeSlot(start=start, end=end),
    )


@pytest.mark.asyncio
async def test_save_and_find_booking(db_session: AsyncSession) -> None:
    space_repo = SQLAlchemySpaceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    booking_repo = SQLAlchemyBookingRepository(db_session)

    space = make_space()
    user = make_user()
    await space_repo.save(space)
    await user_repo.save(user)

    booking = make_booking(space.id, user.id)
    await booking_repo.save(booking)

    found = await booking_repo.find_by_id(booking.id)
    assert found is not None
    assert found.id == booking.id
    assert found.status == BookingStatus.PENDING


@pytest.mark.asyncio
async def test_find_booking_not_found(db_session: AsyncSession) -> None:
    repo = SQLAlchemyBookingRepository(db_session)
    found = await repo.find_by_id(BookingId.generate())
    assert found is None


@pytest.mark.asyncio
async def test_find_bookings_by_user(db_session: AsyncSession) -> None:
    space_repo = SQLAlchemySpaceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    booking_repo = SQLAlchemyBookingRepository(db_session)

    space = make_space()
    user = make_user()
    await space_repo.save(space)
    await user_repo.save(user)

    booking1 = make_booking(space.id, user.id, offset_days=0)
    booking2 = make_booking(space.id, user.id, offset_days=5)
    await booking_repo.save(booking1)
    await booking_repo.save(booking2)

    bookings = await booking_repo.find_by_user(user.id)
    booking_ids = [b.id for b in bookings]
    assert booking1.id in booking_ids
    assert booking2.id in booking_ids


@pytest.mark.asyncio
async def test_find_conflicts(db_session: AsyncSession) -> None:
    space_repo = SQLAlchemySpaceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    booking_repo = SQLAlchemyBookingRepository(db_session)

    space = make_space()
    user = make_user()
    await space_repo.save(space)
    await user_repo.save(user)

    booking = make_booking(space.id, user.id)
    await booking_repo.save(booking)

    conflicts = await booking_repo.find_conflicts(
        space_id=space.id,
        time_slot=booking.time_slot,
    )
    assert len(conflicts) >= 1


@pytest.mark.asyncio
async def test_no_conflicts_different_space(db_session: AsyncSession) -> None:
    space_repo = SQLAlchemySpaceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    booking_repo = SQLAlchemyBookingRepository(db_session)

    space1 = make_space()
    space2 = make_space()
    user = make_user()
    await space_repo.save(space1)
    await space_repo.save(space2)
    await user_repo.save(user)

    booking = make_booking(space1.id, user.id)
    await booking_repo.save(booking)

    conflicts = await booking_repo.find_conflicts(
        space_id=space2.id,
        time_slot=booking.time_slot,
    )
    assert len(conflicts) == 0


@pytest.mark.asyncio
async def test_update_booking_status(db_session: AsyncSession) -> None:
    space_repo = SQLAlchemySpaceRepository(db_session)
    user_repo = SQLAlchemyUserRepository(db_session)
    booking_repo = SQLAlchemyBookingRepository(db_session)

    space = make_space()
    user = make_user()
    await space_repo.save(space)
    await user_repo.save(user)

    booking = make_booking(space.id, user.id)
    await booking_repo.save(booking)

    booking.confirm()
    await booking_repo.update(booking)

    found = await booking_repo.find_by_id(booking.id)
    assert found is not None
    assert found.status == BookingStatus.CONFIRMED
