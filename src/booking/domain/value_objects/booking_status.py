from enum import Enum


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    def can_cancel(self) -> bool:
        return self in (BookingStatus.PENDING, BookingStatus.CONFIRMED)

    def can_confirm(self) -> bool:
        return self == BookingStatus.PENDING
