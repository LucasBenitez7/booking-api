from typing import Protocol

from booking.domain.entities.booking import Booking
from booking.domain.entities.user import User


class NotificationService(Protocol):
    async def send_confirmation(self, booking: Booking, user: User) -> None: ...

    async def send_reminder(self, booking: Booking, user: User) -> None: ...

    async def send_cancellation(self, booking: Booking, user: User) -> None: ...
