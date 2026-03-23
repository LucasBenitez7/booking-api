from dataclasses import dataclass, field
from datetime import UTC, datetime

from booking.domain.events.booking_cancelled import BookingCancelled
from booking.domain.events.booking_created import BookingCreated
from booking.domain.exceptions.booking_errors import UnauthorizedError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot


@dataclass
class Booking:
    id: BookingId
    space_id: BookingId
    user_id: BookingId
    time_slot: TimeSlot
    status: BookingStatus = BookingStatus.PENDING
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    _events: list[BookingCreated | BookingCancelled] = field(
        default_factory=list, repr=False
    )

    def __post_init__(self) -> None:
        event = BookingCreated(
            booking_id=str(self.id),
            space_id=str(self.space_id),
            user_id=str(self.user_id),
            start=self.time_slot.start,
            end=self.time_slot.end,
        )
        self._events.append(event)

    def cancel(self, cancelled_by: BookingId, reason: str | None = None) -> None:
        if not self.status.can_cancel():
            raise ValueError(f"Cannot cancel booking with status '{self.status.value}'")
        if cancelled_by != self.user_id:
            raise UnauthorizedError("Only the booking owner can cancel it")
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now(tz=UTC)
        event = BookingCancelled(
            booking_id=str(self.id),
            space_id=str(self.space_id),
            user_id=str(self.user_id),
            reason=reason,
        )
        self._events.append(event)

    def confirm(self) -> None:
        if not self.status.can_confirm():
            raise ValueError(
                f"Cannot confirm booking with status '{self.status.value}'"
            )
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now(tz=UTC)

    def pull_events(self) -> list[BookingCreated | BookingCancelled]:
        events = list(self._events)
        self._events.clear()
        return events
