import json
from datetime import datetime

import redis.asyncio as redis

from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO

_KEY_PREFIX = "availability"


def _cache_key(space_id: str, start: datetime, end: datetime) -> str:
    return f"{_KEY_PREFIX}:{space_id}:{start.isoformat()}:{end.isoformat()}"


def _invalidation_pattern(space_id: str) -> str:
    return f"{_KEY_PREFIX}:{space_id}:*"


class RedisAvailabilityCache:
    def __init__(self, client: redis.Redis) -> None:
        self._client = client

    async def get(
        self, space_id: str, start: datetime, end: datetime
    ) -> AvailabilityResponseDTO | None:
        raw = await self._client.get(_cache_key(space_id, start, end))
        if raw is None:
            return None
        data = json.loads(raw)
        return AvailabilityResponseDTO(
            space_id=data["space_id"],
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            is_available=data["is_available"],
            conflicting_slots=[
                (datetime.fromisoformat(s), datetime.fromisoformat(e))
                for s, e in data["conflicting_slots"]
            ],
        )

    async def set(
        self,
        space_id: str,
        start: datetime,
        end: datetime,
        result: AvailabilityResponseDTO,
        ttl_seconds: int,
    ) -> None:
        payload = json.dumps(
            {
                "space_id": result.space_id,
                "start": result.start.isoformat(),
                "end": result.end.isoformat(),
                "is_available": result.is_available,
                "conflicting_slots": [
                    [s.isoformat(), e.isoformat()] for s, e in result.conflicting_slots
                ],
            }
        )
        await self._client.setex(_cache_key(space_id, start, end), ttl_seconds, payload)

    async def invalidate(self, space_id: str) -> None:
        pattern = _invalidation_pattern(space_id)
        # SCAN instead of KEYS to avoid blocking Redis in production
        cursor: int = 0
        while True:
            cursor, keys = await self._client.scan(cursor, match=pattern, count=100)
            if keys:
                await self._client.delete(*keys)
            if cursor == 0:
                break
