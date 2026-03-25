from datetime import UTC, datetime

from booking.application.dtos.booking_dtos import UpdateBookingDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.exceptions.booking_errors import (
    BookingConflictError,
    BookingNotFoundError,
    InvalidTimeSlotError,
    SpaceNotFoundError,
    UnauthorizedError,
    UserNotFoundError,
)
from booking.domain.ports.availability_cache import AvailabilityCache
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.ports.space_repository import SpaceRepository
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


class UpdateBookingUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
        space_repository: SpaceRepository,
        user_repository: UserRepository,
        availability_cache: AvailabilityCache,
    ) -> None:
        self._booking_repo = booking_repository
        self._space_repo = space_repository
        self._user_repo = user_repository
        self._cache = availability_cache

    async def execute(self, dto: UpdateBookingDTO) -> BookingResponseDTO:
        booking_id = BookingId.from_string(dto.booking_id)
        requesting_user_id = BookingId.from_string(dto.requesting_user_id)

        booking = await self._booking_repo.find_by_id(booking_id)
        if booking is None:
            raise BookingNotFoundError(dto.booking_id)

        user = await self._user_repo.find_by_id(requesting_user_id)
        if user is None:
            raise UserNotFoundError(dto.requesting_user_id)

        if not user.is_admin and requesting_user_id != booking.user_id:
            raise UnauthorizedError("Only the booking owner or an admin can update it")

        if dto.start < datetime.now(tz=UTC):
            raise InvalidTimeSlotError("Booking cannot start in the past")

        new_time_slot = TimeSlot(start=dto.start, end=dto.end)
        space = await self._space_repo.find_by_id(booking.space_id)
        if space is None:
            raise SpaceNotFoundError(str(booking.space_id))
        space.validate_booking_slot(new_time_slot, datetime.now(tz=UTC))

        conflicts = await self._booking_repo.find_conflicts(
            space_id=booking.space_id,
            time_slot=new_time_slot,
            exclude_booking_id=booking_id,
        )
        if conflicts:
            raise BookingConflictError(
                space_id=str(booking.space_id),
                start=dto.start.isoformat(),
                end=dto.end.isoformat(),
            )

        booking.update_time_slot(new_time_slot=new_time_slot, notes=dto.notes)

        await self._booking_repo.update(booking)
        await self._cache.invalidate(str(booking.space_id))

        return BookingResponseDTO(
            id=str(booking.id),
            space_id=str(booking.space_id),
            user_id=str(booking.user_id),
            start=booking.time_slot.start,
            end=booking.time_slot.end,
            status=booking.status.value,
            notes=booking.notes,
            created_at=booking.created_at,
        )
