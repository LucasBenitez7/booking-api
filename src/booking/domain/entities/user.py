from dataclasses import dataclass, field
from datetime import UTC, datetime

from booking.domain.value_objects.booking_id import BookingId
from booking.domain.value_objects.email import Email


@dataclass
class User:
    id: BookingId
    email: Email
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def promote_to_admin(self) -> None:
        self.is_admin = True
