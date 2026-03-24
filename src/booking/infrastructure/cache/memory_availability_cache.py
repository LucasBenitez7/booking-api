"""In-process availability cache for development and testing without Redis."""

import time
from datetime import datetime

from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO

_CacheEntry = tuple[AvailabilityResponseDTO, float]  # (result, expires_at)


class MemoryAvailabilityCache:
    def __init__(self) -> None:
        self._store: dict[str, _CacheEntry] = {}

    def _key(self, space_id: str, start: datetime, end: datetime) -> str:
        return f"{space_id}:{start.isoformat()}:{end.isoformat()}"

    async def get(
        self, space_id: str, start: datetime, end: datetime
    ) -> AvailabilityResponseDTO | None:
        entry = self._store.get(self._key(space_id, start, end))
        if entry is None:
            return None
        result, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[self._key(space_id, start, end)]
            return None
        return result

    async def set(
        self,
        space_id: str,
        start: datetime,
        end: datetime,
        result: AvailabilityResponseDTO,
        ttl_seconds: int,
    ) -> None:
        key = self._key(space_id, start, end)
        self._store[key] = (result, time.monotonic() + ttl_seconds)

    async def invalidate(self, space_id: str) -> None:
        prefix = f"{space_id}:"
        keys_to_delete = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_delete:
            del self._store[k]
