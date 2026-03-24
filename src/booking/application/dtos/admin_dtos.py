from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class CreateSpaceAdminDTO:
    name: str
    description: str
    capacity: int
    price_per_hour: float


@dataclass(frozen=True)
class UpdateSpaceAdminDTO:
    space_id: str
    name: str | None = None
    description: str | None = None
    capacity: int | None = None
    price_per_hour: float | None = None
    min_duration_minutes: int | None = None
    max_duration_minutes: int | None = None
    min_advance_minutes: int | None = None
    cancellation_deadline_hours: int | None = None
    opening_time: time | None = None
    closing_time: time | None = None
    is_active: bool | None = None


@dataclass(frozen=True)
class UpdateUserAdminDTO:
    user_id: str
    max_active_bookings: int | None = None
    is_admin: bool | None = None


@dataclass(frozen=True)
class ListAdminBookingsDTO:
    status: str | None = None
