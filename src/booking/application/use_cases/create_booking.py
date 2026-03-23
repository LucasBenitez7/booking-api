from booking.application.dtos.booking_dtos import CreateBookingDTO
from booking.application.dtos.booking_response_dto import BookingResponseDTO
from booking.domain.entities.booking import Booking
from booking.domain.exceptions.booking_errors import (
    BookingConflictError,
    SpaceNotFoundError,
    UserNotFoundError,
)
from booking.domain.ports.booking_repository import BookingRepository
from booking.domain.ports.notification_service import NotificationService
from booking.domain.ports.space_repository import SpaceRepository
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.time_slot import TimeSlot


class CreateBookingUseCase:
    def __init__(
        self,
        booking_repository: BookingRepository,
        space_repository: SpaceRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
    ) -> None:
        self._booking_repo = booking_repository
        self._space_repo = space_repository
        self._user_repo = user_repository
        self._notification_service = notification_service

    async def execute(self, dto: CreateBookingDTO) -> BookingResponseDTO:
        space_id = BookingId.from_string(dto.space_id)
        user_id = BookingId.from_string(dto.user_id)

        space = await self._space_repo.find_by_id(space_id)
        if space is None:
            raise SpaceNotFoundError(dto.space_id)

        if not space.is_active:
            raise SpaceNotFoundError(dto.space_id)

        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(dto.user_id)

        time_slot = TimeSlot(start=dto.start, end=dto.end)

        conflicts = await self._booking_repo.find_conflicts(
            space_id=space_id,
            time_slot=time_slot,
        )
        if conflicts:
            raise BookingConflictError(
                space_id=dto.space_id,
                start=dto.start.isoformat(),
                end=dto.end.isoformat(),
            )

        booking = Booking(
            id=BookingId.generate(),
            space_id=space_id,
            user_id=user_id,
            time_slot=time_slot,
            notes=dto.notes,
        )

        await self._booking_repo.save(booking)
        await self._notification_service.send_confirmation(booking, user)

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
