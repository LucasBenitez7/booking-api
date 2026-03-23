from booking.application.dtos.booking_dtos import GetAvailabilityDTO
from booking.application.dtos.booking_response_dto import AvailabilityResponseDTO
from booking.domain.exceptions.booking_errors import SpaceNotFoundError
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.ports.space_repository import SpaceRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


class GetAvailabilityUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
        space_repository: SpaceRepository,
    ) -> None:
        self._booking_repo = booking_repository
        self._space_repo = space_repository

    async def execute(self, dto: GetAvailabilityDTO) -> AvailabilityResponseDTO:
        space_id = BookingId.from_string(dto.space_id)

        space = await self._space_repo.find_by_id(space_id)
        if space is None:
            raise SpaceNotFoundError(dto.space_id)

        time_slot = TimeSlot(start=dto.start, end=dto.end)

        conflicts = await self._booking_repo.find_conflicts(
            space_id=space_id,
            time_slot=time_slot,
        )

        return AvailabilityResponseDTO(
            space_id=dto.space_id,
            start=dto.start,
            end=dto.end,
            is_available=len(conflicts) == 0,
            conflicting_slots=[(c.time_slot.start, c.time_slot.end) for c in conflicts],
        )
