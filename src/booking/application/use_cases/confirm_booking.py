from booking.application.dtos.booking_dtos import ConfirmBookingDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.exceptions.booking_errors import BookingNotFoundError
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.value_objects.booking_id import BookingId


class ConfirmBookingUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
    ) -> None:
        self._booking_repo = booking_repository

    async def execute(self, dto: ConfirmBookingDTO) -> BookingResponseDTO:
        bid = BookingId.from_string(dto.booking_id)

        booking = await self._booking_repo.find_by_id(bid)
        if booking is None:
            raise BookingNotFoundError(dto.booking_id)

        booking.confirm()
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
