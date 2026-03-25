from datetime import time
from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.admin_dtos import CreateSpaceAdminDTO, UpdateSpaceAdminDTO
from booking.application.use_cases.admin_spaces import (
    CreateSpaceUseCase,
    DeleteSpaceUseCase,
    UpdateSpaceUseCase,
)
from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.value_objects.booking_id import BookingId


def make_space(sid: BookingId | None = None) -> Space:
    return Space(
        id=sid or BookingId.generate(),
        name="Room",
        description="D",
        capacity=5,
        price_per_hour=10.0,
    )


@pytest.mark.asyncio
async def test_create_space_saves_and_returns() -> None:
    repo = AsyncMock()
    use_case = CreateSpaceUseCase(space_repository=repo)
    dto = CreateSpaceAdminDTO(
        name="Room A",
        description="desc",
        capacity=8,
        price_per_hour=12.5,
    )

    space = await use_case.execute(dto)

    assert space.name == "Room A"
    assert space.capacity == 8
    repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_space_updates_space() -> None:
    sid = BookingId.generate()
    existing = make_space(sid)
    repo = AsyncMock()
    repo.find_by_id.return_value = existing
    use_case = UpdateSpaceUseCase(space_repository=repo)

    dto = UpdateSpaceAdminDTO(
        space_id=str(sid),
        name="New Name",
        opening_time=time(9, 0),
        closing_time=time(21, 0),
    )

    result = await use_case.execute(dto)

    assert result.name == "New Name"
    assert result.opening_time == time(9, 0)
    assert result.closing_time == time(21, 0)
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_space_not_found_raises() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None
    use_case = UpdateSpaceUseCase(space_repository=repo)

    dto = UpdateSpaceAdminDTO(space_id=str(BookingId.generate()), name="X")

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_delete_space_deactivates() -> None:
    sid = BookingId.generate()
    existing = make_space(sid)
    repo = AsyncMock()
    repo.find_by_id.return_value = existing
    use_case = DeleteSpaceUseCase(space_repository=repo)

    await use_case.execute(str(sid))

    assert existing.is_active is False
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_space_not_found_raises() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None
    use_case = DeleteSpaceUseCase(space_repository=repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(str(BookingId.generate()))
