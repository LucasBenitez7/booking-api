import secrets

from booking.application.dtos.auth_dtos import RequestPasswordResetDTO
from booking.domain.ports.notification_service import NotificationService
from booking.domain.ports.password_reset_token_store import PasswordResetTokenStore
from booking.domain.ports.user_repository import UserRepository
from booking.domain.value_objects.email import Email


class RequestPasswordResetUseCase:
    def __init__(
        self,
        user_repository: UserRepository,
        token_store: PasswordResetTokenStore,
        notification_service: NotificationService,
        token_ttl_seconds: int,
    ) -> None:
        self._user_repo = user_repository
        self._token_store = token_store
        self._notification_service = notification_service
        self._token_ttl_seconds = token_ttl_seconds

    async def execute(self, dto: RequestPasswordResetDTO) -> None:
        """Always succeeds from the caller's perspective (no email enumeration)."""
        try:
            email = Email(dto.email.strip().lower())
        except ValueError:
            return
        user = await self._user_repo.find_by_email(email)
        if user is None:
            return
        token = secrets.token_urlsafe(32)
        await self._token_store.store(
            token=token,
            user_id=str(user.id),
            ttl_seconds=self._token_ttl_seconds,
        )
        await self._notification_service.send_password_reset_email(
            str(email),
            token,
        )
