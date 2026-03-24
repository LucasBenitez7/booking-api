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
        if dto.name is not None:
            space.name = dto.name
        if dto.description is not None:
            space.description = dto.description
        if dto.capacity is not None:
            space.capacity = dto.capacity
        if dto.price_per_hour is not None:
            space.price_per_hour = dto.price_per_hour
        if dto.min_duration_minutes is not None:
            space.min_duration_minutes = dto.min_duration_minutes
        if dto.max_duration_minutes is not None:
            space.max_duration_minutes = dto.max_duration_minutes
        if dto.min_advance_minutes is not None:
            space.min_advance_minutes = dto.min_advance_minutes
        if dto.cancellation_deadline_hours is not None:
            space.cancellation_deadline_hours = dto.cancellation_deadline_hours
        if dto.opening_time is not None:
            space.opening_time = dto.opening_time
        if dto.closing_time is not None:
            space.closing_time = dto.closing_time
        if dto.is_active is not None:
            if dto.is_active:
                space.activate()
            else:
                space.deactivate()
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
