from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta

from booking.domain.exceptions.booking_errors import InvalidTimeSlotError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


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
            raise ValueError("min_duration_minutes cannot exceed max_duration_minutes")
        if self.opening_time >= self.closing_time:
            raise ValueError("opening_time must be before closing_time")

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        capacity: int | None = None,
        price_per_hour: float | None = None,
        min_duration_minutes: int | None = None,
        max_duration_minutes: int | None = None,
        min_advance_minutes: int | None = None,
        cancellation_deadline_hours: int | None = None,
        opening_time: time | None = None,
        closing_time: time | None = None,
        is_active: bool | None = None,
    ) -> None:
        """Apply partial updates and re-validate all invariants."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if capacity is not None:
            self.capacity = capacity
        if price_per_hour is not None:
            self.price_per_hour = price_per_hour
        if min_duration_minutes is not None:
            self.min_duration_minutes = min_duration_minutes
        if max_duration_minutes is not None:
            self.max_duration_minutes = max_duration_minutes
        if min_advance_minutes is not None:
            self.min_advance_minutes = min_advance_minutes
        if cancellation_deadline_hours is not None:
            self.cancellation_deadline_hours = cancellation_deadline_hours
        if opening_time is not None:
            self.opening_time = opening_time
        if closing_time is not None:
            self.closing_time = closing_time
        if is_active is not None:
            self.is_active = is_active
        # Re-run invariant checks so the entity can never be left in an invalid state
        self.__post_init__()

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def validate_booking_slot(self, time_slot: TimeSlot, now: datetime) -> None:
        """Enforce all booking rules: duration, advance booking, and opening hours."""
        duration = time_slot.duration_minutes()
        if duration < self.min_duration_minutes:
            raise InvalidTimeSlotError(
                f"Booking must be at least {self.min_duration_minutes} minutes"
            )
        if duration > self.max_duration_minutes:
            raise InvalidTimeSlotError(
                f"Booking cannot exceed {self.max_duration_minutes} minutes"
            )
        earliest_start = now + timedelta(minutes=self.min_advance_minutes)
        if time_slot.start < earliest_start:
            raise InvalidTimeSlotError(
                f"Booking must start at least {self.min_advance_minutes} minutes from now"
            )
        slot_date = time_slot.start.date()
        if time_slot.start.time() < self.opening_time:
            raise InvalidTimeSlotError(
                f"Booking starts before space opens at {self.opening_time}"
            )
        closing_dt = datetime.combine(
            slot_date, self.closing_time, tzinfo=time_slot.start.tzinfo
        )
        if time_slot.end > closing_dt:
            raise InvalidTimeSlotError(
                f"Booking ends after space closes at {self.closing_time}"
            )

    def validate_cancellation(self, start: datetime, now: datetime) -> None:
        """Raise CancellationDeadlineError if the cancellation window has passed."""
        from booking.domain.exceptions.booking_errors import CancellationDeadlineError

        deadline = start - timedelta(hours=self.cancellation_deadline_hours)
        if now >= deadline:
            raise CancellationDeadlineError(self.cancellation_deadline_hours)
