from booking.application.dtos.booking_dtos import ListUserBookingsDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.exceptions.booking_errors import InvalidBookingStatusFilterError
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.booking_status import BookingStatus


class ListUserBookingsUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
    ) -> None:
        self._booking_repo = booking_repository

    async def execute(self, dto: ListUserBookingsDTO) -> list[BookingResponseDTO]:
        user_id = BookingId.from_string(dto.user_id)

        status: BookingStatus | None = None
        if dto.status is not None:
            try:
                status = BookingStatus(dto.status)
            except ValueError as exc:
                raise InvalidBookingStatusFilterError(dto.status) from exc

        bookings = await self._booking_repo.find_by_user(
            user_id=user_id,
            status=status,
        )

        return [
            BookingResponseDTO(
                id=str(b.id),
                space_id=str(b.space_id),
                user_id=str(b.user_id),
                start=b.time_slot.start,
                end=b.time_slot.end,
                status=b.status.value,
                notes=b.notes,
                created_at=b.created_at,
            )
            for b in bookings
        ]
