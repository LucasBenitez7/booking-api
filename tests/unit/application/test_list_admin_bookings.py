from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.admin_dtos import ListAdminBookingsDTO
from booking.application.use_cases.list_admin_bookings import ListAdminBookingsUseCase
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


@pytest.mark.asyncio
async def test_list_admin_bookings_no_filter() -> None:
    b = make_booking()
    repo = AsyncMock()
    repo.find_all.return_value = [b]
    use_case = ListAdminBookingsUseCase(booking_repository=repo)

    result = await use_case.execute(ListAdminBookingsDTO(status=None))

    assert len(result) == 1
    repo.find_all.assert_awaited_once_with(status=None)


@pytest.mark.asyncio
async def test_list_admin_bookings_with_status() -> None:
    b = make_booking()
    repo = AsyncMock()
    repo.find_all.return_value = [b]
    use_case = ListAdminBookingsUseCase(booking_repository=repo)

    await use_case.execute(
        ListAdminBookingsDTO(status=BookingStatus.CONFIRMED.value),
    )

    repo.find_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_admin_bookings_invalid_status_raises() -> None:
    repo = AsyncMock()
    use_case = ListAdminBookingsUseCase(booking_repository=repo)

    with pytest.raises(InvalidBookingStatusFilterError):
        await use_case.execute(ListAdminBookingsDTO(status="invalid"))
