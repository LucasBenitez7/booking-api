from datetime import UTC, datetime, timedelta

import pytest

from booking.domain.value_objects.time_slot import TimeSlot

FUTURE = datetime(2099, 1, 1, 10, 0, tzinfo=UTC)
FUTURE_END = datetime(2099, 1, 1, 11, 0, tzinfo=UTC)


def test_valid_time_slot() -> None:
    slot = TimeSlot(start=FUTURE, end=FUTURE_END)
    assert slot.start == FUTURE
    assert slot.end == FUTURE_END


def test_duration_minutes() -> None:
    slot = TimeSlot(start=FUTURE, end=FUTURE_END)
    assert slot.duration_minutes() == 60.0


def test_start_must_be_before_end() -> None:
    with pytest.raises(ValueError, match="Start datetime must be before end datetime"):
        TimeSlot(start=FUTURE_END, end=FUTURE)


def test_equal_start_and_end_raises() -> None:
    with pytest.raises(ValueError, match="Start datetime must be before end datetime"):
        TimeSlot(start=FUTURE, end=FUTURE)


def test_timezone_aware_required_on_start() -> None:
    naive = datetime(2099, 1, 1, 10, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        TimeSlot(start=naive, end=FUTURE_END)


def test_timezone_aware_required_on_end() -> None:
    naive_end = datetime(2099, 1, 1, 11, 0)
    with pytest.raises(ValueError, match="timezone-aware"):
        TimeSlot(start=FUTURE, end=naive_end)


def test_past_start_is_valid() -> None:
    past_start = datetime(2000, 1, 1, 10, 0, tzinfo=UTC)
    past_end = datetime(2000, 1, 1, 11, 0, tzinfo=UTC)
    slot = TimeSlot(start=past_start, end=past_end)
    assert slot.start == past_start


def test_overlaps_true() -> None:
    slot_a = TimeSlot(start=FUTURE, end=FUTURE_END)
    slot_b = TimeSlot(
        start=FUTURE + timedelta(minutes=30),
        end=FUTURE_END + timedelta(minutes=30),
    )
    assert slot_a.overlaps(slot_b) is True


def test_overlaps_false() -> None:
    slot_a = TimeSlot(start=FUTURE, end=FUTURE_END)
    slot_b = TimeSlot(
        start=FUTURE_END,
        end=FUTURE_END + timedelta(hours=1),
    )
    assert slot_a.overlaps(slot_b) is False


def test_overlaps_contained() -> None:
    slot_a = TimeSlot(start=FUTURE, end=FUTURE_END)
    slot_b = TimeSlot(
        start=FUTURE + timedelta(minutes=15),
        end=FUTURE + timedelta(minutes=45),
    )
    assert slot_a.overlaps(slot_b) is True
