from booking.application.dtos.auth_dtos import ConfirmPasswordResetDTO
from booking.domain.exceptions.auth_errors import (
    InvalidPasswordResetTokenError,
    WeakPasswordError,
)
from booking.domain.ports.password_hasher import PasswordHasher
from booking.domain.ports.password_reset_token_store import PasswordResetTokenStore
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.password_policy import MIN_PASSWORD_LENGTH


class ConfirmPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_store: PasswordResetTokenStore,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repository
        self._token_store = token_store
        self._password_hasher = password_hasher

    async def execute(self, dto: ConfirmPasswordResetDTO) -> None:
        if len(dto.new_password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(MIN_PASSWORD_LENGTH)
        user_id_str = await self._token_store.consume(dto.token)
        if user_id_str is None:
            raise InvalidPasswordResetTokenError()
        user_id = BookingId.from_string(user_id_str)
        user = await self._user_repo.find_by_id(user_id)
        if user is None:
            raise InvalidPasswordResetTokenError()
        user.hashed_password = await self._password_hasher.hash_password(
            dto.new_password
        )
        await self._user_repo.update(user)
