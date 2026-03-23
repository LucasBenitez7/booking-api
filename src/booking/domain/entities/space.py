from dataclasses import dataclass, field
from datetime import UTC, datetime

from booking.domain.value_objects.booking_id import BookingId


@dataclass
class Space:
    id: BookingId
    name: str
    description: str
    capacity: int
    price_per_hour: float
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        if self.price_per_hour < 0:
            raise ValueError("Price per hour cannot be negative")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True
