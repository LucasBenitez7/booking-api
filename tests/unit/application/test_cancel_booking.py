from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import CancelBookingDTO
from booking.application.use_cases.cancel_booking import CancelBookingUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    UserNotFoundError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email("lucas@example.com"),
        full_name="Lucas Benítez",
        hashed_password="hashed",
    )


def make_booking(user_id: BookingId) -> Booking:
    return Booking(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=user_id,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
    )


@pytest.mark.asyncio
async def test_cancel_booking_success() -> None:
    user = make_user()
    booking = make_booking(user_id=user.id)

    booking_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock()
    booking_repo.find_by_id.return_value = booking
    user_repo.find_by_id.return_value = user

    use_case = CancelBookingUseCase(
        booking_repository=booking_repo,
        user_repository=user_repo,
        notification_service=notification_service,
    )

    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(user.id),
        reason="Changed plans",
    )

    result = await use_case.execute(dto)

    assert result.status == BookingStatus.CANCELLED.value
    booking_repo.update.assert_called_once()
    notification_service.send_cancellation.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_booking_not_found() -> None:
    booking_repo = AsyncMock()
    user_repo = AsyncMock()
    booking_repo.find_by_id.return_value = None

    use_case = CancelBookingUseCase(
        booking_repository=booking_repo,
        user_repository=user_repo,
        notification_service=AsyncMock(),
    )

    dto = CancelBookingDTO(
        booking_id=str(BookingId.generate()),
        cancelled_by=str(BookingId.generate()),
    )

    with pytest.raises(BookingNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_cancel_booking_user_not_found() -> None:
    user = make_user()
    booking = make_booking(user_id=user.id)

    booking_repo = AsyncMock()
    user_repo = AsyncMock()
    booking_repo.find_by_id.return_value = booking
    user_repo.find_by_id.return_value = None

    use_case = CancelBookingUseCase(
        booking_repository=booking_repo,
        user_repository=user_repo,
        notification_service=AsyncMock(),
    )

    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(BookingId.generate()),
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)
