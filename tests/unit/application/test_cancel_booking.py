from datetime import UTC, datetime, time
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.booking_dtos import CancelBookingDTO
from booking.application.use_cases.cancel_booking import CancelBookingUseCase
from booking.domain.entities.booking import Booking
from booking.domain.entities.space import Space
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    CancellationDeadlineError,
    UserNotFoundError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_user(is_admin: bool = False) -> User:
    return User(
        id=BookingId.generate(),
        email=Email("lucas@example.com"),
        full_name="Lucas Benítez",
        hashed_password="hashed",
        is_admin=is_admin,
    )


def make_space(space_id: BookingId, cancellation_deadline_hours: int = 24) -> Space:
    return Space(
        id=space_id,
        name="Room A",
        description="",
        capacity=10,
        price_per_hour=10.0,
        cancellation_deadline_hours=cancellation_deadline_hours,
        opening_time=time(8, 0),
        closing_time=time(22, 0),
    )


def make_booking(user_id: BookingId, space_id: BookingId | None = None) -> Booking:
    sid = space_id or BookingId.generate()
    return Booking.reconstitute(
        id=BookingId.generate(),
        space_id=sid,
        user_id=user_id,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
    )


def make_use_case(
    booking: Booking | None,
    user: User | None,
    space: Space | None = None,
) -> CancelBookingUseCase:
    booking_repo = AsyncMock()
    space_repo = AsyncMock()
    user_repo = AsyncMock()
    notification_service = AsyncMock()
    booking_repo.find_by_id.return_value = booking
    user_repo.find_by_id.return_value = user
    space_repo.find_by_id.return_value = space
    return CancelBookingUseCase(
        booking_repository=booking_repo,
        space_repository=space_repo,
        user_repository=user_repo,
        notification_service=notification_service,
    )


@pytest.mark.asyncio
async def test_cancel_booking_success() -> None:
    user = make_user()
    space_id = BookingId.generate()
    booking = make_booking(user_id=user.id, space_id=space_id)
    space = make_space(space_id, cancellation_deadline_hours=0)  # no deadline

    use_case = make_use_case(booking, user, space)
    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(user.id),
        reason="Changed plans",
    )

    result = await use_case.execute(dto)

    assert result.status == BookingStatus.CANCELLED.value
    use_case._booking_repo.update.assert_called_once()  # type: ignore[attr-defined]
    use_case._notification_service.send_cancellation.assert_called_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_cancel_booking_deadline_exceeded_raises() -> None:
    user = make_user()
    space_id = BookingId.generate()
    # Start is very far in the future but deadline is huge — simulate by using a near past start
    near_start = datetime(2020, 1, 1, 10, 0, tzinfo=UTC)  # already past
    booking = Booking.reconstitute(
        id=BookingId.generate(),
        space_id=space_id,
        user_id=user.id,
        time_slot=TimeSlot(start=near_start, end=datetime(2020, 1, 1, 11, 0, tzinfo=UTC)),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=near_start,
        updated_at=near_start,
    )
    space = make_space(space_id, cancellation_deadline_hours=24)

    use_case = make_use_case(booking, user, space)
    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(user.id),
    )

    with pytest.raises(CancellationDeadlineError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_admin_can_cancel_past_deadline() -> None:
    admin = make_user(is_admin=True)
    space_id = BookingId.generate()
    near_start = datetime(2020, 1, 1, 10, 0, tzinfo=UTC)
    booking = Booking.reconstitute(
        id=BookingId.generate(),
        space_id=space_id,
        user_id=BookingId.generate(),
        time_slot=TimeSlot(start=near_start, end=datetime(2020, 1, 1, 11, 0, tzinfo=UTC)),
        status=BookingStatus.CONFIRMED,
        notes=None,
        created_at=near_start,
        updated_at=near_start,
    )
    space = make_space(space_id, cancellation_deadline_hours=24)

    use_case = make_use_case(booking, admin, space)
    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(admin.id),
    )

    result = await use_case.execute(dto)
    assert result.status == BookingStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_cancel_booking_not_found() -> None:
    use_case = make_use_case(None, None)
    dto = CancelBookingDTO(
        booking_id=str(BookingId.generate()),
        cancelled_by=str(BookingId.generate()),
    )

    with pytest.raises(BookingNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_cancel_booking_user_not_found() -> None:
    user = make_user()
    space_id = BookingId.generate()
    booking = make_booking(user_id=user.id, space_id=space_id)

    use_case = make_use_case(booking, None)
    dto = CancelBookingDTO(
        booking_id=str(booking.id),
        cancelled_by=str(BookingId.generate()),
    )

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)
