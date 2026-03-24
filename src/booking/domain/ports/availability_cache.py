from datetime import datetime
from typing import Protocol

from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO


class AvailabilityCache(Protocol):
    async def get(
        self, space_id: str, start: datetime, end: datetime
    ) -> AvailabilityResponseDTO | None: ...

    async def set(
        self,
        space_id: str,
        start: datetime,
        end: datetime,
        result: AvailabilityResponseDTO,
        ttl_seconds: int,
    ) -> None: ...

    async def invalidate(self, space_id: str) -> None: ...
