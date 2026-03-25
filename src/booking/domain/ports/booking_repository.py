from typing import Protocol

from booking.domain.entities.booking import Booking
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus
from booking.domain.value_objects.time_slot import TimeSlot


class BookingRepository(Protocol):
    async def save(self, booking: Booking) -> None: ...

    async def find_by_id(self, booking_id: BookingId) -> Booking | None: ...

    async def find_by_user(
        self,
        user_id: BookingId,
        status: BookingStatus | None = None,
    ) -> list[Booking]: ...

    async def find_conflicts(
        self,
        space_id: BookingId,
        time_slot: TimeSlot,
        exclude_booking_id: BookingId | None = None,
    ) -> list[Booking]:
        """Return bookings that overlap with time_slot, excluding CANCELLED and EXPIRED."""
        ...

    async def update(self, booking: Booking) -> None: ...

    async def find_all(
        self,
        status: BookingStatus | None = None,
        limit: int = 500,  # safety cap — full pagination is a future concern
        offset: int = 0,
    ) -> list[Booking]: ...

    async def count_active_by_user(self, user_id: BookingId) -> int: ...
