from booking.application.dtos.admin_dtos import UpdateUserAdminDTO
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import UserNotFoundError
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId


class UpdateUserAdminUseCase:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    async def execute(self, dto: UpdateUserAdminDTO) -> User:
        user_id = BookingId.from_string(dto.user_id)
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(dto.user_id)
        if dto.max_active_bookings is not None:
            user.max_active_bookings = dto.max_active_bookings
        if dto.is_admin is not None:
            user.is_admin = dto.is_admin
        await self._user_repo.update(user)
        return user
