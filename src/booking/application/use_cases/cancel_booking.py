from booking.application.dtos.booking_dtos import CancelBookingDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.exceptions.booking_errors import (
    BookingNotFoundError,
    UserNotFoundError,
)
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.ports.notification_service import NotificationService
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId


class CancelBookingUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ) -> None:
        self._booking_repo = booking_repository
        self._user_repo = user_repository
        self._notification_service = notification_service

    async def execute(self, dto: CancelBookingDTO) -> BookingResponseDTO:
        booking_id = BookingId.from_string(dto.booking_id)
        cancelled_by = BookingId.from_string(dto.cancelled_by)

        booking = await self._booking_repo.find_by_id(booking_id)
        if booking is None:
            raise BookingNotFoundError(dto.booking_id)

        user = await self._user_repo.find_by_id(cancelled_by)
        if user is None:
            raise UserNotFoundError(dto.cancelled_by)

        booking.cancel(
            cancelled_by=cancelled_by, reason=dto.reason, is_admin=user.is_admin
        )
        await self._booking_repo.update(booking)
        await self._notification_service.send_cancellation(booking, user)

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
