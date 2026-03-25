from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class BookingUpdated:
    booking_id: str
    space_id: str
    user_id: str
    start: datetime
    end: datetime
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
