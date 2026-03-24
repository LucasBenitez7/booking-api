from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.auth_dtos import LoginUserDTO
from booking.application.use_cases.login_user import LoginUserUseCase
from booking.domain.entities.user import User
from booking.domain.exceptions.auth_errors import AuthenticationError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


def make_user(email: str = "user@example.com", is_active: bool = True) -> User:
    return User(
        id=BookingId.generate(),
        email=Email(email),
        full_name="Test User",
        hashed_password="stored-hash",
        is_active=is_active,
    )


def make_use_case(
    user: User | None = None,
) -> tuple[LoginUserUseCase, AsyncMock, AsyncMock]:
    user_repo = AsyncMock()
    password_hasher = AsyncMock()
    if user is not None:
        user_repo.find_by_email.return_value = user
    else:
        user_repo.find_by_email.return_value = None
    password_hasher.verify_password.return_value = True
    use_case = LoginUserUseCase(
        user_repository=user_repo,
        password_hasher=password_hasher,
    )
    return use_case, user_repo, password_hasher


@pytest.mark.asyncio
async def test_login_user_success() -> None:
    user = make_user()
    use_case, user_repo, password_hasher = make_use_case(user)

    dto = LoginUserDTO(
        email="  USER@Example.COM ",
        password="correctpass",
    )
    result = await use_case.execute(dto)

    assert result.id == user.id
    user_repo.find_by_email.assert_awaited_once()
    password_hasher.verify_password.assert_awaited_once_with(
        "correctpass", "stored-hash"
    )


@pytest.mark.asyncio
async def test_login_user_unknown_email_raises() -> None:
    use_case, _, _ = make_use_case(user=None)

    dto = LoginUserDTO(email="no@example.com", password="x")

    with pytest.raises(AuthenticationError, match="Invalid email or password"):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_login_user_inactive_raises() -> None:
    user = make_user(is_active=False)
    use_case, _, _ = make_use_case(user)

    dto = LoginUserDTO(email="user@example.com", password="x")

    with pytest.raises(AuthenticationError, match="Account is disabled"):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_login_user_wrong_password_raises() -> None:
    user = make_user()
    use_case, _, password_hasher = make_use_case(user)
    password_hasher.verify_password.return_value = False

    dto = LoginUserDTO(email="user@example.com", password="wrong")

    with pytest.raises(AuthenticationError, match="Invalid email or password"):
        await use_case.execute(dto)
