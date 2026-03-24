from unittest.mock import AsyncMock

import pytest

from booking.application.dtos.admin_dtos import UpdateUserAdminDTO
from booking.application.use_cases.update_user_admin import UpdateUserAdminUseCase
from booking.domain.entities.user import User
from booking.domain.exceptions.booking_errors import UserNotFoundError
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


def make_user() -> User:
    return User(
        id=BookingId.generate(),
        email=Email("u@example.com"),
        full_name="U",
        hashed_password="h",
        max_active_bookings=5,
        is_admin=False,
    )


@pytest.mark.asyncio
async def test_update_user_admin_max_active_bookings() -> None:
    user = make_user()
    repo = AsyncMock()
    repo.find_by_id.return_value = user
    use_case = UpdateUserAdminUseCase(user_repository=repo)

    dto = UpdateUserAdminDTO(user_id=str(user.id), max_active_bookings=10)
    result = await use_case.execute(dto)

    assert result.max_active_bookings == 10
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_admin_promote_admin() -> None:
    user = make_user()
    repo = AsyncMock()
    repo.find_by_id.return_value = user
    use_case = UpdateUserAdminUseCase(user_repository=repo)

    dto = UpdateUserAdminDTO(user_id=str(user.id), is_admin=True)
    result = await use_case.execute(dto)

    assert result.is_admin is True
    repo.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_admin_not_found_raises() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None
    use_case = UpdateUserAdminUseCase(user_repository=repo)

    dto = UpdateUserAdminDTO(user_id=str(BookingId.generate()))

    with pytest.raises(UserNotFoundError):
        await use_case.execute(dto)
