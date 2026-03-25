from pydantic import BaseModel, Field


class AdminUserUpdateBody(BaseModel):
    max_active_bookings: int | None = Field(default=None, ge=1, le=1000)
    is_admin: bool | None = None
