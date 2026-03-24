from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import GetBookingDTO
from booking.application.use_cases.get_booking import GetBookingUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_booking(user_id: BookingId) -> Booking:
    return Booking.reconstitute(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=user_id,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


def make_user(uid: BookingId, *, is_admin: bool = False) -> User:
    return User(
        id=uid,
        email=Email("viewer@example.com"),
        full_name="Viewer",
        hashed_password="h",
        is_admin=is_admin,
    )


def make_use_case(
    booking: Booking | None,
    user: User | None,
) -> GetBookingUseCase:
    booking_repo = AsyncMock()
    user_repo = AsyncMock()
    booking_repo.find_by_id.return_value = booking
    user_repo.find_by_id.return_value = user
    return GetBookingUseCase(
        booking_repository=booking_repo,
        user_repository=user_repo,
    )


@pytest.mark.asyncio
async def test_get_booking_owner_success() -> None:
    owner_id = BookingId.generate()
    booking = make_booking(owner_id)
    viewer = make_user(owner_id, is_admin=False)
    use_case = make_use_case(booking, viewer)

    dto = GetBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(owner_id),
    )
    result = await use_case.execute(dto)

    assert result.id == str(booking.id)
    assert result.status == BookingStatus.CONFIRMED.value


@pytest.mark.asyncio
async def test_get_booking_admin_can_view_any() -> None:
    owner_id = BookingId.generate()
    admin_id = BookingId.generate()
    booking = make_booking(owner_id)
    admin = make_user(admin_id, is_admin=True)
    use_case = make_use_case(booking, admin)

    dto = GetBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(admin_id),
    )
    result = await use_case.execute(dto)

    assert result.id == str(booking.id)


@pytest.mark.asyncio
async def test_get_booking_not_found_raises() -> None:
    viewer = make_user(BookingId.generate())
    use_case = make_use_case(None, viewer)

    dto = GetBookingDTO(
        booking_id=str(BookingId.generate()),
        requesting_user_id=str(viewer.id),
    )

    with pytest.raises(BookingNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_get_booking_requesting_user_not_found_raises() -> None:
    owner_id = BookingId.generate()
    booking = make_booking(owner_id)
    use_case = make_use_case(booking, None)

    dto = GetBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(BookingId.generate()),
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_get_booking_non_owner_non_admin_raises() -> None:
    owner_id = BookingId.generate()
    other_id = BookingId.generate()
    booking = make_booking(owner_id)
    other = make_user(other_id, is_admin=False)
    use_case = make_use_case(booking, other)

    dto = GetBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(other_id),
    )

    with pytest.raises(UnauthorizedError):
        await use_case.execute(dto)
