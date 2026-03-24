from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class BookingExpired:
    booking_id: str
    space_id: str
    user_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
