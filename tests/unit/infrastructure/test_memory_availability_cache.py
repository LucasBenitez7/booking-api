import asyncio
from datetime import UTC, datetime

import pytest

from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO
from booking.infrastructure.cache.memory_availability_cache import (
    MemoryAvailabilityCache,
)

START = datetime(2099, 6, 1, 10, 0, tzinfo=UTC)
END = datetime(2099, 6, 1, 11, 0, tzinfo=UTC)
SPACE_ID = "space-abc"


def make_result(available: bool = True) -> AvailabilityResponseDTO:
    return AvailabilityResponseDTO(
        space_id=SPACE_ID,
        start=START,
        end=END,
        is_available=available,
        conflicting_slots=[],
    )


@pytest.mark.asyncio
async def test_cache_miss_returns_none() -> None:
    cache = MemoryAvailabilityCache()
    assert await cache.get(SPACE_ID, START, END) is None


@pytest.mark.asyncio
async def test_cache_set_and_get() -> None:
    cache = MemoryAvailabilityCache()
    result = make_result()
    await cache.set(SPACE_ID, START, END, result, ttl_seconds=60)
    cached = await cache.get(SPACE_ID, START, END)
    assert cached is not None
    assert cached.is_available is True


@pytest.mark.asyncio
async def test_cache_ttl_expiry() -> None:
    cache = MemoryAvailabilityCache()
    result = make_result()
    await cache.set(SPACE_ID, START, END, result, ttl_seconds=0)
    # Sleep briefly to let the TTL expire (0s TTL expires immediately)
    await asyncio.sleep(0.01)
    assert await cache.get(SPACE_ID, START, END) is None


@pytest.mark.asyncio
async def test_cache_invalidate_removes_space_entries() -> None:
    cache = MemoryAvailabilityCache()
    result = make_result()
    other_start = datetime(2099, 6, 2, 10, 0, tzinfo=UTC)
    other_end = datetime(2099, 6, 2, 11, 0, tzinfo=UTC)

    await cache.set(SPACE_ID, START, END, result, ttl_seconds=60)
    await cache.set(SPACE_ID, other_start, other_end, result, ttl_seconds=60)
    await cache.set("other-space", START, END, result, ttl_seconds=60)

    await cache.invalidate(SPACE_ID)

    assert await cache.get(SPACE_ID, START, END) is None
    assert await cache.get(SPACE_ID, other_start, other_end) is None
    # Other space must not be affected
    assert await cache.get("other-space", START, END) is not None


@pytest.mark.asyncio
async def test_cache_invalidate_noop_when_empty() -> None:
    cache = MemoryAvailabilityCache()
    await cache.invalidate(SPACE_ID)  # should not raise
