from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import AuthenticationError
from booking.domain.ports.auth_token_issuer import AuthTokenIssuer
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.booking_id import BookingId


class RefreshAccessTokenUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_issuer: AuthTokenIssuer,
    ) -> None:
        self._user_repo = user_repository
        self._tokens = token_issuer

    async def execute(self, refresh_token: str) -> tuple[str, User]:
        user_id_str = self._tokens.decode_refresh_token(refresh_token)
        user_id = BookingId.from_string(user_id_str)
        user = await self._user_repo.find_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid or expired session")
        access = self._tokens.create_access_token(user_id_str)
        return access, user
