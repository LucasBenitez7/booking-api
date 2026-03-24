from datetime import datetime

from pydantic import BaseModel


class BookingPublic(BaseModel):
    id: str
    space_id: str
    user_id: str
    start: datetime
    end: datetime
    status: str
    notes: str | None
    created_at: datetime


class CreateBookingBody(BaseModel):
    space_id: str
    start: datetime
    end: datetime
    notes: str | None = None


class UpdateBookingBody(BaseModel):
    start: datetime
    end: datetime
    notes: str | None = None
