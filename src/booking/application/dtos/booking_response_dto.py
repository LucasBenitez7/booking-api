from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BookingResponseDTO:
    id: str
    space_id: str
    user_id: str
    start: datetime
    end: datetime
    status: str
    notes: str | None
    created_at: datetime


@dataclass(frozen=True)
class AvailabilityResponseDTO:
    space_id: str
    start: datetime
    end: datetime
    is_available: bool
    conflicting_slots: list[tuple[datetime, datetime]]
