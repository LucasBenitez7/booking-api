from datetime import UTC, datetime

from booking.application.dtos.booking_dtos import UpdateBookingDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    InvalidTimeSlotError,
    UnauthorizedError,
    UserNotFoundError,
)
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


class UpdateBookingUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
        user_repository: UserRepository,
    ) -> None:
        self._booking_repo = booking_repository
        self._user_repo = user_repository

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
        booking.update_time_slot(new_time_slot=new_time_slot, notes=dto.notes)

        await self._booking_repo.update(booking)

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
