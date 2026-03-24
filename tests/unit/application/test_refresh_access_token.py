from unittest.mock import AsyncMock, MagicMock

import pytest

from booking.application.use_cases.refresh_access_token import RefreshAccessTokenUseCase
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import AuthenticationError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


def make_user(*, active: bool = True) -> User:
    return User(
        id=BookingId.generate(),
        email=Email("u@example.com"),
        full_name="U",
        hashed_password="h",
        is_active=active,
    )


def make_use_case(
    user: User | None,
) -> tuple[RefreshAccessTokenUseCase, AsyncMock, MagicMock]:
    user_repo = AsyncMock()
    user_repo.find_by_id.return_value = user
    tokens = MagicMock()
    tokens.decode_refresh_token.return_value = (
        str(user.id) if user is not None else str(BookingId.generate())
    )
    tokens.create_access_token.return_value = "new-access-token"
    use_case = RefreshAccessTokenUseCase(
        user_repository=user_repo,
        token_issuer=tokens,
    )
    return use_case, user_repo, tokens


@pytest.mark.asyncio
async def test_refresh_access_token_success() -> None:
    user = make_user()
    use_case, user_repo, tokens = make_use_case(user)

    access, returned_user = await use_case.execute("refresh-token")

    assert access == "new-access-token"
    assert returned_user.id == user.id
    tokens.decode_refresh_token.assert_called_once_with("refresh-token")
    tokens.create_access_token.assert_called_once_with(str(user.id))
    user_repo.find_by_id.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_access_token_user_missing_raises() -> None:
    use_case, _, _ = make_use_case(None)

    with pytest.raises(AuthenticationError, match="Invalid or expired session"):
        await use_case.execute("refresh-token")


@pytest.mark.asyncio
async def test_refresh_access_token_inactive_user_raises() -> None:
    user = make_user(active=False)
    use_case, _, _ = make_use_case(user)

    with pytest.raises(AuthenticationError, match="Invalid or expired session"):
        await use_case.execute("refresh-token")
