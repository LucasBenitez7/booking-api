from datetime import UTC, datetime

import pytest

from booking.domain.entities.booking import Booking
from booking.domain.events.booking_cancelled import BookingCancelled
from booking.domain.events.booking_created import BookingCreated
from booking.domain.events.booking_updated import BookingUpdated
from booking.domain.exceptions.booking_errors import UnauthorizedError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot

FUTURE_START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)
FUTURE_START_2 = datetime(2099, 6, 2, 10, 0, tzinfo=UTC)
FUTURE_END_2 = datetime(2099, 6, 2, 11, 0, tzinfo=UTC)


def make_booking(user_id: BookingId | None = None) -> Booking:
    uid = user_id or BookingId.generate()
    return Booking(
        id=BookingId.generate(),
        space_id=BookingId.generate(),
        user_id=uid,
        time_slot=TimeSlot(start=FUTURE_START, end=FUTURE_END),
    )


def test_booking_created_with_confirmed_status() -> None:
    booking = make_booking()
    assert booking.status == BookingStatus.CONFIRMED


def test_booking_emits_created_event() -> None:
    booking = make_booking()
    events = booking.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], BookingCreated)


def test_pull_events_clears_events() -> None:
    booking = make_booking()
    booking.pull_events()
    assert booking.pull_events() == []


def test_cancel_booking() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.cancel(cancelled_by=user_id, reason="No longer needed")
    assert booking.status == BookingStatus.CANCELLED


def test_cancel_emits_cancelled_event() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.pull_events()
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


def test_admin_can_cancel_any_booking() -> None:
    owner_id = BookingId.generate()
    booking = make_booking(user_id=owner_id)
    admin_id = BookingId.generate()
    booking.cancel(cancelled_by=admin_id, is_admin=True)
    assert booking.status == BookingStatus.CANCELLED


def test_update_time_slot() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    new_slot = TimeSlot(start=FUTURE_START_2, end=FUTURE_END_2)
    booking.update_time_slot(new_slot)
    assert booking.time_slot == new_slot


def test_update_time_slot_emits_event() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.pull_events()
    new_slot = TimeSlot(start=FUTURE_START_2, end=FUTURE_END_2)
    booking.update_time_slot(new_slot)
    events = booking.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], BookingUpdated)


def test_update_notes() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    new_slot = TimeSlot(start=FUTURE_START_2, end=FUTURE_END_2)
    booking.update_time_slot(new_slot, notes="New note")
    assert booking.notes == "New note"


def test_update_cancelled_booking_raises() -> None:
    user_id = BookingId.generate()
    booking = make_booking(user_id=user_id)
    booking.cancel(cancelled_by=user_id)
    new_slot = TimeSlot(start=FUTURE_START_2, end=FUTURE_END_2)
    with pytest.raises(ValueError, match="Cannot update booking"):
        booking.update_time_slot(new_slot)
