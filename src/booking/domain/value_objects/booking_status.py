from enum import Enum


class BookingStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    def can_cancel(self) -> bool:
        return self == BookingStatus.CONFIRMED

    def can_expire(self) -> bool:
        return self == BookingStatus.CONFIRMED
