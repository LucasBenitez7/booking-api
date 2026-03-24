from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.auth_dtos import RegisterUserDTO
from booking.application.use_cases.register_user import RegisterUserUseCase
from booking.domain.exceptions.auth_errors import (
    EmailAlreadyRegisteredError,
    WeakPasswordError,
)


def make_use_case() -> tuple[RegisterUserUseCase, AsyncMock, AsyncMock]:
    user_repo = AsyncMock()
    password_hasher = AsyncMock()
    password_hasher.hash_password.return_value = "hashed-secret"
    use_case = RegisterUserUseCase(
        user_repository=user_repo,
        password_hasher=password_hasher,
    )
    return use_case, user_repo, password_hasher


@pytest.mark.asyncio
async def test_register_user_success() -> None:
    use_case, user_repo, password_hasher = make_use_case()
    user_repo.find_by_email.return_value = None

    dto = RegisterUserDTO(
        email="  NEW@Example.COM ",
        password="securepass1",
        full_name="  Jane Doe ",
    )
    user = await use_case.execute(dto)

    assert str(user.email) == "new@example.com"
    assert user.full_name == "Jane Doe"
    assert user.hashed_password == "hashed-secret"
    password_hasher.hash_password.assert_awaited_once_with("securepass1")
    user_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_weak_password_raises() -> None:
    use_case, user_repo, _ = make_use_case()

    dto = RegisterUserDTO(
        email="a@b.com",
        password="short",
        full_name="X",
    )

    with pytest.raises(WeakPasswordError):
        await use_case.execute(dto)

    user_repo.find_by_email.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_duplicate_email_raises() -> None:
    use_case, user_repo, _ = make_use_case()
    existing = AsyncMock()
    user_repo.find_by_email.return_value = existing

    dto = RegisterUserDTO(
        email="dup@example.com",
        password="securepass1",
        full_name="X",
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        await use_case.execute(dto)

    user_repo.save.assert_not_called()
