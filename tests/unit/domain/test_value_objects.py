import pytest

from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.email import Email


def test_booking_id_generate() -> None:
    bid = BookingId.generate()
    assert bid is not None
    assert str(bid) != ""


def test_booking_id_from_string() -> None:
    bid = BookingId.generate()
    restored = BookingId.from_string(str(bid))
    assert bid == restored


def test_booking_id_invalid_string_raises() -> None:
    with pytest.raises(ValueError):
        BookingId.from_string("not-a-uuid")


def test_booking_id_is_immutable() -> None:
    bid = BookingId.generate()
    with pytest.raises(AttributeError):
        bid.value = None  # type: ignore[misc, assignment]


def test_email_valid() -> None:
    email = Email("lucas@example.com")
    assert str(email) == "lucas@example.com"


def test_email_invalid_raises() -> None:
    with pytest.raises(ValueError, match="Invalid email address"):
        Email("not-an-email")


def test_email_is_immutable() -> None:
    email = Email("lucas@example.com")
    with pytest.raises(AttributeError):
        email.value = "other@example.com"  # type: ignore[misc]


def test_booking_status_can_cancel_pending() -> None:
    assert BookingStatus.PENDING.can_cancel() is True


def test_booking_status_can_cancel_confirmed() -> None:
    assert BookingStatus.CONFIRMED.can_cancel() is True


def test_booking_status_cannot_cancel_cancelled() -> None:
    assert BookingStatus.CANCELLED.can_cancel() is False


def test_booking_status_can_confirm_pending() -> None:
    assert BookingStatus.PENDING.can_confirm() is True


def test_booking_status_cannot_confirm_confirmed() -> None:
    assert BookingStatus.CONFIRMED.can_confirm() is False


def test_booking_status_cannot_confirm_cancelled() -> None:
    assert BookingStatus.CANCELLED.can_confirm() is False
