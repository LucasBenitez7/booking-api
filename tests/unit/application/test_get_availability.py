from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import GetAvailabilityDTO
from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO
from booking.application.use_cases.get_availability import GetAvailabilityUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
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
    now = datetime.now(tz=UTC)
    return Booking.reconstitute(
        id=BookingId.generate(),
        space_id=space_id,
        user_id=BookingId.generate(),
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=now,
        updated_at=now,
    )


def make_use_case(
    space: Space | None = None,
    conflicts: list[Booking] | None = None,
    cached: AvailabilityResponseDTO | None = None,
) -> tuple[GetAvailabilityUseCase, AsyncMock, AsyncMock, AsyncMock]:
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    cache = AsyncMock()

    space_repo.find_by_id.return_value = space or make_space()
    booking_repo.find_conflicts.return_value = conflicts or []
    cache.get.return_value = cached  # None = cache miss by default

    use_case = GetAvailabilityUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
        cache=cache,
    )
    return use_case, booking_repo, space_repo, cache


@pytest.mark.asyncio
async def test_availability_is_available() -> None:
    use_case, booking_repo, space_repo, cache = make_use_case()

    dto = GetAvailabilityDTO(
        space_id=str(BookingId.generate()), start=FUTURE_START, end=FUTURE_END
    )
    result = await use_case.execute(dto)

    assert result.is_available is True
    assert result.conflicting_slots == []
    cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_availability_has_conflicts() -> None:
    space = make_space()
    booking = make_booking(space_id=space.id)
    use_case, _, _, cache = make_use_case(space=space, conflicts=[booking])

    dto = GetAvailabilityDTO(space_id=str(space.id), start=FUTURE_START, end=FUTURE_END)
    result = await use_case.execute(dto)

    assert result.is_available is False
    assert len(result.conflicting_slots) == 1
    assert result.conflicting_slots[0] == (FUTURE_START, FUTURE_END)
    cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_availability_returns_cached_result() -> None:
    space_id = str(BookingId.generate())
    cached_result = AvailabilityResponseDTO(
        space_id=space_id,
        start=FUTURE_START,
        end=FUTURE_END,
        is_available=True,
        conflicting_slots=[],
    )
    use_case, booking_repo, space_repo, cache = make_use_case(cached=cached_result)

    dto = GetAvailabilityDTO(space_id=space_id, start=FUTURE_START, end=FUTURE_END)
    result = await use_case.execute(dto)

    assert result is cached_result
    # DB should not be hit when cache returns a result
    space_repo.find_by_id.assert_not_called()
    booking_repo.find_conflicts.assert_not_called()
    cache.set.assert_not_called()


@pytest.mark.asyncio
async def test_availability_space_not_found() -> None:
    use_case, _, space_repo, _ = make_use_case()
    space_repo.find_by_id.return_value = None

    dto = GetAvailabilityDTO(
        space_id=str(BookingId.generate()),
        start=FUTURE_START,
        end=FUTURE_END,
    )

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(dto)
