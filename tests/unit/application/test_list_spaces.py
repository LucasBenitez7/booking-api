from unittest.mock import AsyncMock

import pytest

from booking.application.use_cases.list_spaces import GetSpaceUseCase, ListSpacesUseCase
from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.value_objects.booking_id import BookingId


def make_space(*, active: bool = True) -> Space:
    return Space(
        id=BookingId.generate(),
        name="S",
        description="D",
        capacity=4,
        price_per_hour=1.0,
        is_active=active,
    )


@pytest.mark.asyncio
async def test_list_spaces_returns_active_only() -> None:
    spaces = [make_space()]
    repo = AsyncMock()
    repo.find_all.return_value = spaces
    use_case = ListSpacesUseCase(space_repository=repo)

    result = await use_case.execute()

    assert result == spaces
    repo.find_all.assert_awaited_once_with(active_only=True)


@pytest.mark.asyncio
async def test_get_space_success() -> None:
    space = make_space()
    repo = AsyncMock()
    repo.find_by_id.return_value = space
    use_case = GetSpaceUseCase(space_repository=repo)

    result = await use_case.execute(str(space.id))

    assert result.id == space.id


@pytest.mark.asyncio
async def test_get_space_not_found_raises() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None
    use_case = GetSpaceUseCase(space_repository=repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(str(BookingId.generate()))


@pytest.mark.asyncio
async def test_get_space_inactive_raises() -> None:
    space = make_space(active=False)
    repo = AsyncMock()
    repo.find_by_id.return_value = space
    use_case = GetSpaceUseCase(space_repository=repo)

    with pytest.raises(SpaceNotFoundError):
        await use_case.execute(str(space.id))
