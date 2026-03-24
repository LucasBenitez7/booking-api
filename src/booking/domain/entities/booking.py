from dataclasses import dataclass, field
from datetime import UTC, datetime

from booking.domain.events.booking_cancelled import BookingCancelled
from booking.domain.events.booking_created import BookingCreated
from booking.domain.events.booking_updated import BookingUpdated
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
    status: BookingStatus = BookingStatus.CONFIRMED
    notes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    _events: list[BookingCreated | BookingCancelled | BookingUpdated] = field(
        default_factory=list, repr=False
    )

    @classmethod
    def create(
        cls,
        id: BookingId,
        space_id: BookingId,
        user_id: BookingId,
        time_slot: TimeSlot,
        notes: str | None = None,
    ) -> "Booking":
        """Create a brand-new booking and emit BookingCreated."""
        booking = cls(
            id=id,
            space_id=space_id,
            user_id=user_id,
            time_slot=time_slot,
            notes=notes,
        )
        booking._events.append(
            BookingCreated(
                booking_id=str(id),
                space_id=str(space_id),
                user_id=str(user_id),
                start=time_slot.start,
                end=time_slot.end,
            )
        )
        return booking

    @classmethod
    def reconstitute(
        cls,
        id: BookingId,
        space_id: BookingId,
        user_id: BookingId,
        time_slot: TimeSlot,
        status: BookingStatus,
        notes: str | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> "Booking":
        """Rehydrate from persistence — no events emitted."""
        return cls(
            id=id,
            space_id=space_id,
            user_id=user_id,
            time_slot=time_slot,
            status=status,
            notes=notes,
            created_at=created_at,
            updated_at=updated_at,
        )

    def is_modifiable(self) -> bool:
        return self.status == BookingStatus.CONFIRMED

    def cancel(
        self,
        cancelled_by: BookingId,
        reason: str | None = None,
        is_admin: bool = False,
    ) -> None:
        if not self.status.can_cancel():
            raise ValueError(f"Cannot cancel booking with status '{self.status.value}'")
        if not is_admin and cancelled_by != self.user_id:
            raise UnauthorizedError("Only the booking owner can cancel it")
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now(tz=UTC)
        self._events.append(
            BookingCancelled(
                booking_id=str(self.id),
                space_id=str(self.space_id),
                user_id=str(self.user_id),
                reason=reason,
            )
        )

    def update_time_slot(
        self, new_time_slot: TimeSlot, notes: str | None = None
    ) -> None:
        if not self.is_modifiable():
            raise ValueError(f"Cannot update booking with status '{self.status.value}'")
        self.time_slot = new_time_slot
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now(tz=UTC)
        self._events.append(
            BookingUpdated(
                booking_id=str(self.id),
                space_id=str(self.space_id),
                user_id=str(self.user_id),
                start=new_time_slot.start,
                end=new_time_slot.end,
            )
        )

    def pull_events(self) -> list[BookingCreated | BookingCancelled | BookingUpdated]:
        events = list(self._events)
        self._events.clear()
        return events
