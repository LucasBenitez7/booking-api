from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.ports.space_repository import SpaceRepository
from booking.domain.value_objects.booking_id import BookingId


class ListSpacesUseCase:
    def __init__(self, space_repository: SpaceRepository) -> None:
        self._space_repo = space_repository

    async def execute(self) -> list[Space]:
        return await self._space_repo.find_all(active_only=True)


class GetSpaceUseCase:
    def __init__(self, space_repository: SpaceRepository) -> None:
        self._space_repo = space_repository

    async def execute(self, space_id: str) -> Space:
        space = await self._space_repo.find_by_id(BookingId.from_string(space_id))
        if space is None or not space.is_active:
            raise SpaceNotFoundError(space_id)
        return space
