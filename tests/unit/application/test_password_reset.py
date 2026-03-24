from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.auth_dtos import (
    ConfirmPasswordResetDTO,
    RequestPasswordResetDTO,
)
from booking.application.use_cases.confirm_password_reset import (
    ConfirmPasswordResetUseCase,
)
from booking.application.use_cases.request_password_reset import (
    RequestPasswordResetUseCase,
)
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import (
    InvalidPasswordResetTokenError,
    WeakPasswordError,
)
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email("user@example.com"),
        full_name="U",
        hashed_password="old-hash",
    )


# --- RequestPasswordReset ---


@pytest.mark.asyncio
async def test_request_password_reset_invalid_email_noop() -> None:
    user_repo = AsyncMock()
    token_store = AsyncMock()
    notification = AsyncMock()
    use_case = RequestPasswordResetUseCase(
        user_repository=user_repo,
        token_store=token_store,
        notification_service=notification,
        token_ttl_seconds=1800,
    )

    await use_case.execute(RequestPasswordResetDTO(email="not-an-email"))

    user_repo.find_by_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_password_reset_unknown_user_noop() -> None:
    user_repo = AsyncMock()
    user_repo.find_by_email.return_value = None
    token_store = AsyncMock()
    notification = AsyncMock()
    use_case = RequestPasswordResetUseCase(
        user_repository=user_repo,
        token_store=token_store,
        notification_service=notification,
        token_ttl_seconds=1800,
    )

    await use_case.execute(RequestPasswordResetDTO(email="nobody@example.com"))

    token_store.store.assert_not_called()
    notification.send_password_reset_email.assert_not_called()


@pytest.mark.asyncio
async def test_request_password_reset_stores_token_and_sends_email() -> None:
    user = make_user()
    user_repo = AsyncMock()
    user_repo.find_by_email.return_value = user
    token_store = AsyncMock()
    notification = AsyncMock()
    use_case = RequestPasswordResetUseCase(
        user_repository=user_repo,
        token_store=token_store,
        notification_service=notification,
        token_ttl_seconds=1800,
    )

    await use_case.execute(RequestPasswordResetDTO(email="  USER@Example.COM "))

    token_store.store.assert_awaited_once()
    notification.send_password_reset_email.assert_awaited_once()


# --- ConfirmPasswordReset ---


@pytest.mark.asyncio
async def test_confirm_password_reset_weak_password_raises() -> None:
    use_case = ConfirmPasswordResetUseCase(
        user_repository=AsyncMock(),
        token_store=AsyncMock(),
        password_hasher=AsyncMock(),
    )

    dto = ConfirmPasswordResetDTO(token="t", new_password="short")

    with pytest.raises(WeakPasswordError):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_confirm_password_reset_invalid_token_raises() -> None:
    token_store = AsyncMock()
    token_store.consume.return_value = None
    use_case = ConfirmPasswordResetUseCase(
        user_repository=AsyncMock(),
        token_store=token_store,
        password_hasher=AsyncMock(),
    )

    with pytest.raises(InvalidPasswordResetTokenError):
        await use_case.execute(
            ConfirmPasswordResetDTO(token="bad", new_password="longenough1"),
        )


@pytest.mark.asyncio
async def test_confirm_password_reset_user_missing_raises() -> None:
    token_store = AsyncMock()
    token_store.consume.return_value = str(BookingId.generate())
    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = None
    use_case = ConfirmPasswordResetUseCase(
        user_repository=user_repo,
        token_store=token_store,
        password_hasher=AsyncMock(),
    )

    with pytest.raises(InvalidPasswordResetTokenError):
        await use_case.execute(
            ConfirmPasswordResetDTO(token="ok", new_password="longenough1"),
        )


@pytest.mark.asyncio
async def test_confirm_password_reset_success() -> None:
    user = make_user()
    token_store = AsyncMock()
    token_store.consume.return_value = str(user.id)
    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = user
    hasher = AsyncMock()
    hasher.hash_password.return_value = "new-hash"
    use_case = ConfirmPasswordResetUseCase(
        user_repository=user_repo,
        token_store=token_store,
        password_hasher=hasher,
    )

    await use_case.execute(
        ConfirmPasswordResetDTO(token="tok", new_password="longenough1"),
    )

    assert user.hashed_password == "new-hash"
    user_repo.update.assert_awaited_once()
