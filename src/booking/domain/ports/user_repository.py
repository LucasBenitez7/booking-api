from typing import Protocol

from booking.domain.entities.user import User
from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


class UserRepository(Protocol):
    async def save(self, user: User) -> None: ...

    async def find_by_id(self, user_id: BookingId) -> User | None: ...

    async def find_by_email(self, email: Email) -> User | None: ...

    async def update(self, user: User) -> None: ...
