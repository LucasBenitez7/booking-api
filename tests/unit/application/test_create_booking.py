from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import CreateBookingDTO
from booking.application.use_cases.create_booking import CreateBookingUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import (
    BookingConflictError,
    InvalidTimeSlotError,
    SpaceNotFoundError,
    UserNotFoundError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_space() -> Space:
    return Space(
        id=BookingId.generate(),
        name="Room A",
        description="Main room",
        capacity=10,
        price_per_hour=50.0,
    )


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email("lucas@example.com"),
        full_name="Lucas Benítez",
        hashed_password="hashed",
    )


def make_use_case(
    space: Space | None = None,
    user: User | None = None,
    conflicts: list[Booking] | None = None,
) -> tuple[CreateBookingUseCase, AsyncMock, AsyncMock, AsyncMock, AsyncMock]:
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock()

    space_repo.find_by_id.return_value = space or make_space()
    user_repo.find_by_id.return_value = user or make_user()
    booking_repo.find_conflicts.return_value = conflicts or []

    use_case = CreateBookingUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
        user_repository=user_repo,
        notification_service=notification_service,
    )
    return use_case, booking_repo, space_repo, user_repo, notification_service


@pytest.mark.asyncio
async def test_create_booking_success() -> None:
    space = make_space()
    user = make_user()
    use_case, booking_repo, _, _, notification_service = make_use_case(
        space=space, user=user
    )

    dto = CreateBookingDTO(
        space_id=str(space.id),
        user_id=str(user.id),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    result = await use_case.execute(dto)

    assert result.status == BookingStatus.CONFIRMED.value
    assert result.space_id == str(space.id)
    assert result.user_id == str(user.id)
    booking_repo.save.assert_called_once()
    notification_service.send_confirmation.assert_called_once()


@pytest.mark.asyncio
async def test_create_booking_space_not_found() -> None:
    use_case, _, space_repo, _, _ = make_use_case()
    space_repo.find_by_id.return_value = None

    dto = CreateBookingDTO(
        space_id=str(BookingId.generate()),
        user_id=str(BookingId.generate()),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_create_booking_user_not_found() -> None:
    space = make_space()
    use_case, _, _, user_repo, _ = make_use_case(space=space)
    user_repo.find_by_id.return_value = None

    dto = CreateBookingDTO(
        space_id=str(space.id),
        user_id=str(BookingId.generate()),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_create_booking_conflict() -> None:
    space = make_space()
    user = make_user()
    existing = Booking(
        id=BookingId.generate(),
        space_id=space.id,
        user_id=user.id,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
    )
    use_case, _, _, _, _ = make_use_case(space=space, user=user, conflicts=[existing])

    dto = CreateBookingDTO(
        space_id=str(space.id),
        user_id=str(user.id),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(BookingConflictError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_create_booking_inactive_space_raises() -> None:
    space = make_space()
    space.deactivate()
    use_case, _, _, _, _ = make_use_case(space=space)

    dto = CreateBookingDTO(
        space_id=str(space.id),
        user_id=str(BookingId.generate()),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_create_booking_past_start_raises() -> None:
    past_start = datetime(2000, 1, 1, 10, 0, tzinfo=UTC)
    past_end = datetime(2000, 1, 1, 11, 0, tzinfo=UTC)
    use_case, _, _, _, _ = make_use_case()

    dto = CreateBookingDTO(
        space_id=str(BookingId.generate()),
        user_id=str(BookingId.generate()),
        start=past_start,
        end=past_end,
    )

    with pytest.raises(InvalidTimeSlotError):
        await use_case.execute(dto)
