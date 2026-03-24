from booking.application.dtos.auth_dtos import LoginUserDTO
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import AuthenticationError
from booking.domain.ports.password_hasher import PasswordHasher
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.email import Email


class LoginUserUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repo = user_repository
        self._password_hasher = password_hasher

    async def execute(self, dto: LoginUserDTO) -> User:
        email = Email(dto.email.strip().lower())
        user = await self._user_repo.find_by_email(email)
        if user is None:
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        if not await self._password_hasher.verify_password(
            dto.password, user.hashed_password
        ):
            raise AuthenticationError("Invalid email or password")
        return user
