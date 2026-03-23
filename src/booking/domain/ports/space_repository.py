from typing import Protocol

from booking.domain.entities.space import Space
from booking.domain.value_objects.booking_id import BookingId


class SpaceRepository(Protocol):
    async def save(self, space: Space) -> None: ...

    async def find_by_id(self, space_id: BookingId) -> Space | None: ...

    async def find_all(self, active_only: bool = True) -> list[Space]: ...

    async def update(self, space: Space) -> None: ...
