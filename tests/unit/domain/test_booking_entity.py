from datetime import UTC, datetime

import pytest

from booking.domain.entities.booking import Booking
from booking.domain.events.booking_cancelled import BookingCancelled
from booking.domain.events.booking_created import BookingCreated
from booking.domain.exceptions.booking_errors import UnauthorizedError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)


def make_booking(user_id: BookingId | None = None) -> Booking:
    uid = user_id or BookingId.generate()
    return Booking(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=uid,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
    )


def test_booking_created_with_pending_status() -> None:
    booking = make_booking()
    assert booking.status == BookingStatus.PENDING


def test_booking_emits_created_event() -> None:
    booking = make_booking()
    events = booking.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], BookingCreated)


def test_pull_events_clears_events() -> None:
    booking = make_booking()
    booking.pull_events()
    assert booking.pull_events() == []


def test_confirm_booking() -> None:
    booking = make_booking()
    booking.confirm()
    assert booking.status == BookingStatus.CONFIRMED


def test_cancel_booking() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.cancel(cancelled_by=user_id, reason="No longer needed")
    assert booking.status == BookingStatus.CANCELLED


def test_cancel_emits_cancelled_event() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.pull_events()  # clear created event
    booking.cancel(cancelled_by=user_id)
    events = booking.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], BookingCancelled)


def test_cancel_already_cancelled_raises() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.cancel(cancelled_by=user_id)
    with pytest.raises(ValueError, match="Cannot cancel booking"):
        booking.cancel(cancelled_by=user_id)


def test_cancel_by_wrong_user_raises() -> None:
    booking = make_booking()
    wrong_user = BookingId.generate()
    with pytest.raises(UnauthorizedError):
        booking.cancel(cancelled_by=wrong_user)


def test_confirm_already_confirmed_raises() -> None:
    booking = make_booking()
    booking.confirm()
    with pytest.raises(ValueError, match="Cannot confirm booking"):
        booking.confirm()
