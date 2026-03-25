from booking.application.dtos.admin_dtos import CreateSpaceAdminDTO, UpdateSpaceAdminDTO
from booking.domain.entities.space import Space
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.ports.space_repository import SpaceRepository
from booking.domain.value_objects.booking_id import BookingId


class CreateSpaceUseCase:
    def __init__(self, space_repository: SpaceRepository) -> None:
        self._space_repo = space_repository

    async def execute(self, dto: CreateSpaceAdminDTO) -> Space:
        space = Space(
            id=BookingId.generate(),
            name=dto.name,
            description=dto.description,
            capacity=dto.capacity,
            price_per_hour=dto.price_per_hour,
        )
        await self._space_repo.save(space)
        return space


class UpdateSpaceUseCase:
    def __init__(self, space_repository: SpaceRepository) -> None:
        self._space_repo = space_repository

    async def execute(self, dto: UpdateSpaceAdminDTO) -> Space:
        space_id = BookingId.from_string(dto.space_id)
        space = await self._space_repo.find_by_id(space_id)
        if space is None:
            raise SpaceNotFoundError(dto.space_id)
        space.update(
            name=dto.name,
            description=dto.description,
            capacity=dto.capacity,
            price_per_hour=dto.price_per_hour,
            min_duration_minutes=dto.min_duration_minutes,
            max_duration_minutes=dto.max_duration_minutes,
            min_advance_minutes=dto.min_advance_minutes,
            cancellation_deadline_hours=dto.cancellation_deadline_hours,
            opening_time=dto.opening_time,
            closing_time=dto.closing_time,
            is_active=dto.is_active,
        )
        await self._space_repo.update(space)
        return space


class DeleteSpaceUseCase:
    def __init__(self, space_repository: SpaceRepository) -> None:
        self._space_repo = space_repository

    async def execute(self, space_id: str) -> None:
        sid = BookingId.from_string(space_id)
        space = await self._space_repo.find_by_id(sid)
        if space is None:
            raise SpaceNotFoundError(space_id)
        space.deactivate()
        await self._space_repo.update(space)
