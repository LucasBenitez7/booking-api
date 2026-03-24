from enum import Enum


class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"

    def can_cancel(self) -> bool:
        return self == BookingStatus.CONFIRMED
