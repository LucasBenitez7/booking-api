from dataclasses import dataclass, field
from datetime import UTC, datetime, time

from booking.domain.value_objects.booking_id import BookingId


@dataclass
class Space:
    id: BookingId
    name: str
    description: str
    capacity: int
    price_per_hour: float
    is_active: bool = True
    min_duration_minutes: int = 30
    max_duration_minutes: int = 480
    min_advance_minutes: int = 60
    cancellation_deadline_hours: int = 24
    opening_time: time = field(default_factory=lambda: time(8, 0))
    closing_time: time = field(default_factory=lambda: time(22, 0))
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        if self.price_per_hour < 0:
            raise ValueError("Price per hour cannot be negative")
        if self.min_duration_minutes <= 0:
            raise ValueError("min_duration_minutes must be positive")
        if self.max_duration_minutes <= 0:
            raise ValueError("max_duration_minutes must be positive")
        if self.min_duration_minutes > self.max_duration_minutes:
            raise ValueError(
                "min_duration_minutes cannot exceed max_duration_minutes"
            )
        if self.opening_time >= self.closing_time:
            raise ValueError("opening_time must be before closing_time")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True
