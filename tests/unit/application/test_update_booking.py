from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import UpdateBookingDTO
from booking.application.use_cases.update_booking import UpdateBookingUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    InvalidTimeSlotError,
    UnauthorizedError,
    UserNotFoundError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus  # noqa: F401
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)
NEW_START = datetime(2099, 6, 2, 10, 0, tzinfo=UTC)
NEW_END = datetime(2099, 6, 2, 11, 0, tzinfo=UTC)


def make_user(is_admin: bool = False) -> User:
    return User(
        id=BookingId.generate(),
        email=Email("user@example.com"),
        full_name="Test User",
        hashed_password="hashed",
        is_admin=is_admin,
    )


def make_booking(user_id: BookingId) -> Booking:

    now = datetime.now(tz=UTC)
    return Booking.reconstitute(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=user_id,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=now,
        updated_at=now,
    )


def make_use_case(
    booking: Booking | None = None,
    user: User | None = None,
) -> tuple[UpdateBookingUseCase, AsyncMock, AsyncMock, AsyncMock]:
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    user_repo = AsyncMock()

    booking_repo.find_by_id.return_value = booking
    user_repo.find_by_id.return_value = user
    if booking is not None:
        space_repo.find_by_id.return_value = Space(
            id=booking.space_id,
            name="Room",
            description="Main",
            capacity=10,
            price_per_hour=50.0,
        )
    booking_repo.find_conflicts.return_value = []

    use_case = UpdateBookingUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
        user_repository=user_repo,
    )
    return use_case, booking_repo, user_repo, space_repo


@pytest.mark.asyncio
async def test_update_booking_success() -> None:
    user = make_user()
    booking = make_booking(user_id=user.id)
    use_case, booking_repo, _, _ = make_use_case(booking=booking, user=user)

    dto = UpdateBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(user.id),
        start=NEW_START,
        end=NEW_END,
        notes="Updated note",
    )

    result = await use_case.execute(dto)

    assert result.status == BookingStatus.CONFIRMED.value
    assert result.start == NEW_START
    assert result.end == NEW_END
    booking_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_booking_not_found() -> None:
    use_case, _, _, _ = make_use_case(booking=None, user=make_user())

    dto = UpdateBookingDTO(
        booking_id=str(BookingId.generate()),
        requesting_user_id=str(BookingId.generate()),
        start=NEW_START,
        end=NEW_END,
    )

    with pytest.raises(BookingNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_update_booking_user_not_found() -> None:
    user = make_user()
    booking = make_booking(user_id=user.id)
    use_case, _, _, _ = make_use_case(booking=booking, user=None)

    dto = UpdateBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(BookingId.generate()),
        start=NEW_START,
        end=NEW_END,
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_update_booking_unauthorized() -> None:
    owner = make_user()
    other_user = make_user()
    booking = make_booking(user_id=owner.id)
    use_case, _, _, _ = make_use_case(booking=booking, user=other_user)

    dto = UpdateBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(other_user.id),
        start=NEW_START,
        end=NEW_END,
    )

    with pytest.raises(UnauthorizedError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_admin_can_update_any_booking() -> None:
    owner = make_user()
    admin = make_user(is_admin=True)
    booking = make_booking(user_id=owner.id)
    use_case, booking_repo, _, _ = make_use_case(booking=booking, user=admin)

    dto = UpdateBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(admin.id),
        start=NEW_START,
        end=NEW_END,
    )

    result = await use_case.execute(dto)
    assert result.start == NEW_START
    booking_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_booking_past_start_raises() -> None:
    user = make_user()
    booking = make_booking(user_id=user.id)
    use_case, _, _, _ = make_use_case(booking=booking, user=user)

    dto = UpdateBookingDTO(
        booking_id=str(booking.id),
        requesting_user_id=str(user.id),
        start=datetime(2000, 1, 1, 10, 0, tzinfo=UTC),
        end=datetime(2000, 1, 1, 11, 0, tzinfo=UTC),
    )

    with pytest.raises(InvalidTimeSlotError):
        await use_case.execute(dto)
