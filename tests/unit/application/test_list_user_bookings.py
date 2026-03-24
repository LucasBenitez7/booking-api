from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import ListUserBookingsDTO
from booking.application.use_cases.list_user_bookings import ListUserBookingsUseCase
from booking.domain.entities.booking import Booking
from booking.domain.exceptions.booking_errors import InvalidBookingStatusFilterError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot

START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_booking() -> Booking:
    return Booking.reconstitute(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=BookingId.generate(),
        time_slot=TimeSlot(start=START, end=END),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


def make_use_case(bookings: list[Booking]) -> ListUserBookingsUseCase:
    repo = AsyncMock()
    repo.find_by_user.return_value = bookings
    return ListUserBookingsUseCase(booking_repository=repo)


@pytest.mark.asyncio
async def test_list_user_bookings_no_filter() -> None:
    b = make_booking()
    use_case = make_use_case([b])
    dto = ListUserBookingsDTO(user_id=str(b.user_id))

    result = await use_case.execute(dto)

    assert len(result) == 1
    assert result[0].id == str(b.id)


@pytest.mark.asyncio
async def test_list_user_bookings_with_status_filter() -> None:
    b = make_booking()
    use_case = make_use_case([b])
    dto = ListUserBookingsDTO(
        user_id=str(b.user_id),
        status=BookingStatus.CONFIRMED.value,
    )

    result = await use_case.execute(dto)

    assert len(result) == 1


@pytest.mark.asyncio
async def test_list_user_bookings_invalid_status_raises() -> None:
    use_case = make_use_case([])
    dto = ListUserBookingsDTO(user_id=str(BookingId.generate()), status="not-a-status")

    with pytest.raises(InvalidBookingStatusFilterError):
        await use_case.execute(dto)
