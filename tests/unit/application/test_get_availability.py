from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import GetAvailabilityDTO
from booking.application.use_cases.get_availability import GetAvailabilityUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.value_objects.booking_id import BookingId
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


def make_booking(space_id: BookingId) -> Booking:
    return Booking(
        id=BookingId.generate(),
        space_id=space_id,
        user_id=BookingId.generate(),
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
    )


@pytest.mark.asyncio
async def test_availability_is_available() -> None:
    space = make_space()
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    space_repo.find_by_id.return_value = space
    booking_repo.find_conflicts.return_value = []

    use_case = GetAvailabilityUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
    )

    dto = GetAvailabilityDTO(
        space_id=str(space.id),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    result = await use_case.execute(dto)

    assert result.is_available is True
    assert result.conflicting_slots == []


@pytest.mark.asyncio
async def test_availability_has_conflicts() -> None:
    space = make_space()
    booking = make_booking(space_id=space.id)

    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    space_repo.find_by_id.return_value = space
    booking_repo.find_conflicts.return_value = [booking]

    use_case = GetAvailabilityUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
    )

    dto = GetAvailabilityDTO(
        space_id=str(space.id),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    result = await use_case.execute(dto)

    assert result.is_available is False
    assert len(result.conflicting_slots) == 1
    assert result.conflicting_slots[0] == (FUTURE_START, FUTURE_END)


@pytest.mark.asyncio
async def test_availability_space_not_found() -> None:
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    space_repo.find_by_id.return_value = None

    use_case = GetAvailabilityUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
    )

    dto = GetAvailabilityDTO(
        space_id=str(BookingId.generate()),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(dto)
