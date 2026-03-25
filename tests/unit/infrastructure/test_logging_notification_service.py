from datetime import UTC, datetime

import pytest

from booking.domain.entities.booking import Booking
from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.time_slot import TimeSlot
from booking.infrastructure.notifications.logging_notification_service import (
    LoggingNotificationService,
)

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


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email("u@example.com"),
        full_name="U",
        hashed_password="h",
    )


@pytest.mark.asyncio
async def test_logging_notification_send_confirmation() -> None:
    svc = LoggingNotificationService()
    await svc.send_confirmation(make_booking(), make_user())


@pytest.mark.asyncio
async def test_logging_notification_send_reminder() -> None:
    svc = LoggingNotificationService()
    await svc.send_reminder(make_booking(), make_user())


@pytest.mark.asyncio
async def test_logging_notification_send_cancellation() -> None:
    svc = LoggingNotificationService()
    await svc.send_cancellation(make_booking(), make_user())


@pytest.mark.asyncio
async def test_logging_notification_send_password_reset_email() -> None:
    svc = LoggingNotificationService()
    await svc.send_password_reset_email("a@b.com", "secret-token-not-logged")
