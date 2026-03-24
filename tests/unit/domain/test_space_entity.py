from datetime import UTC, datetime, time, timedelta

import pytest

from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import (
    CancellationDeadlineError,
    InvalidTimeSlotError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


def make_space(**kwargs: object) -> Space:
    defaults: dict[str, object] = {
        "id": BookingId.generate(),
        "name": "Room A",
        "description": "Desc",
        "capacity": 10,
        "price_per_hour": 25.0,
    }
    defaults.update(kwargs)
    return Space(**defaults)  # type: ignore[arg-type]


# --- __post_init__ ---


def test_space_invalid_capacity_raises() -> None:
    with pytest.raises(ValueError, match="Capacity must be greater than 0"):
        make_space(capacity=0)


def test_space_negative_price_raises() -> None:
    with pytest.raises(ValueError, match="Price per hour cannot be negative"):
        make_space(price_per_hour=-1.0)


def test_space_invalid_min_duration_raises() -> None:
    with pytest.raises(ValueError, match="min_duration_minutes must be positive"):
        make_space(min_duration_minutes=0)


def test_space_invalid_max_duration_raises() -> None:
    with pytest.raises(ValueError, match="max_duration_minutes must be positive"):
        make_space(max_duration_minutes=0)


def test_space_min_greater_than_max_raises() -> None:
    with pytest.raises(
        ValueError, match="min_duration_minutes cannot exceed max_duration_minutes"
    ):
        make_space(min_duration_minutes=120, max_duration_minutes=60)


def test_space_opening_not_before_closing_raises() -> None:
    with pytest.raises(ValueError, match="opening_time must be before closing_time"):
        make_space(opening_time=time(18, 0), closing_time=time(9, 0))


# --- update ---


def test_space_update_revalidates_invariants() -> None:
    space = make_space()
    with pytest.raises(ValueError, match="Capacity must be greater than 0"):
        space.update(capacity=-1)


def test_space_update_partial_preserves_other_fields() -> None:
    space = make_space(name="Old", capacity=10)
    space.update(name="New")
    assert space.name == "New"
    assert space.capacity == 10


# --- activate / deactivate ---


def test_space_deactivate_and_activate() -> None:
    space = make_space()
    space.deactivate()
    assert space.is_active is False
    space.activate()
    assert space.is_active is True


# --- validate_booking_slot ---


def test_validate_booking_slot_duration_too_short() -> None:
    space = make_space(min_duration_minutes=60)
    now = datetime(2099, 6, 1, 8, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 10, 0, tzinfo=UTC),
        end=datetime(2099, 6, 1, 10, 30, tzinfo=UTC),
    )
    with pytest.raises(InvalidTimeSlotError, match="at least 60 minutes"):
        space.validate_booking_slot(slot, now)


def test_validate_booking_slot_duration_too_long() -> None:
    space = make_space(max_duration_minutes=60)
    now = datetime(2099, 6, 1, 8, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 10, 0, tzinfo=UTC),
        end=datetime(2099, 6, 1, 12, 0, tzinfo=UTC),
    )
    with pytest.raises(InvalidTimeSlotError, match="cannot exceed 60 minutes"):
        space.validate_booking_slot(slot, now)


def test_validate_booking_slot_too_soon() -> None:
    space = make_space(min_advance_minutes=120)
    now = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 11, 0, tzinfo=UTC),
        end=datetime(2099, 6, 1, 12, 0, tzinfo=UTC),
    )
    with pytest.raises(InvalidTimeSlotError, match="at least 120 minutes from now"):
        space.validate_booking_slot(slot, now)


def test_validate_booking_slot_before_opening() -> None:
    space = make_space(
        min_advance_minutes=0,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )
    now = datetime(2099, 6, 1, 8, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 8, 30, tzinfo=UTC),
        end=datetime(2099, 6, 1, 9, 30, tzinfo=UTC),
    )
    with pytest.raises(InvalidTimeSlotError, match="before space opens"):
        space.validate_booking_slot(slot, now)


def test_validate_booking_slot_after_closing() -> None:
    space = make_space(
        min_advance_minutes=0,
        opening_time=time(8, 0),
        closing_time=time(18, 0),
    )
    now = datetime(2099, 6, 1, 8, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 17, 0, tzinfo=UTC),
        end=datetime(2099, 6, 1, 19, 0, tzinfo=UTC),
    )
    with pytest.raises(InvalidTimeSlotError, match="after space closes"):
        space.validate_booking_slot(slot, now)


def test_validate_booking_slot_success() -> None:
    space = make_space(
        min_duration_minutes=30,
        max_duration_minutes=480,
        min_advance_minutes=60,
        opening_time=time(8, 0),
        closing_time=time(22, 0),
    )
    now = datetime(2099, 6, 1, 8, 0, tzinfo=UTC)
    slot = TimeSlot(
        start=datetime(2099, 6, 1, 10, 0, tzinfo=UTC),
        end=datetime(2099, 6, 1, 11, 0, tzinfo=UTC),
    )
    space.validate_booking_slot(slot, now)


# --- validate_cancellation ---


def test_validate_cancellation_within_deadline_raises() -> None:
    space = make_space(cancellation_deadline_hours=24)
    start = datetime(2099, 6, 2, 10, 0, tzinfo=UTC)
    now = start - timedelta(hours=12)
    with pytest.raises(CancellationDeadlineError):
        space.validate_cancellation(start, now)


def test_validate_cancellation_before_deadline_ok() -> None:
    space = make_space(cancellation_deadline_hours=24)
    start = datetime(2099, 6, 2, 10, 0, tzinfo=UTC)
    now = start - timedelta(hours=48)
    space.validate_cancellation(start, now)
