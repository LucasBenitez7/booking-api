from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateBookingDTO:
    space_id: str
    user_id: str
    start: datetime
    end: datetime
    notes: str | None = None


@dataclass(frozen=True)
class CancelBookingDTO:
    booking_id: str
    cancelled_by: str
    reason: str | None = None


@dataclass(frozen=True)
class UpdateBookingDTO:
    booking_id: str
    requesting_user_id: str
    start: datetime
    end: datetime
    notes: str | None = None


@dataclass(frozen=True)
class GetAvailabilityDTO:
    space_id: str
    start: datetime
    end: datetime


@dataclass(frozen=True)
class ListUserBookingsDTO:
    user_id: str
    status: str | None = None
