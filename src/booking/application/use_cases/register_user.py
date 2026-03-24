from booking.application.dtos.auth_dtos import RegisterUserDTO
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import (
    EmailAlreadyRegisteredError,
    WeakPasswordError,
)
from booking.domain.ports.password_hasher import PasswordHasher
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email
from booking.domain.value_objects.password_policy import MIN_PASSWORD_LENGTH


class RegisterUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repository
        self._password_hasher = password_hasher

    async def execute(self, dto: RegisterUserDTO) -> User:
        if len(dto.password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(MIN_PASSWORD_LENGTH)

        email = Email(dto.email.strip().lower())
        existing = await self._user_repo.find_by_email(email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(str(email))

        user = User(
            id=BookingId.generate(),
            email=email,
            full_name=dto.full_name.strip(),
            hashed_password=await self._password_hasher.hash_password(dto.password),
        )
        await self._user_repo.save(user)
        return user
