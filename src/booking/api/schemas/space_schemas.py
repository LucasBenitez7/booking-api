from datetime import datetime, time

from pydantic import BaseModel, Field


class SpacePublic(BaseModel):
    id: str
    name: str
    description: str
    capacity: int
    price_per_hour: float
    is_active: bool
    min_duration_minutes: int
    max_duration_minutes: int
    min_advance_minutes: int
    cancellation_deadline_hours: int
    opening_time: time
    closing_time: time
    created_at: datetime

    model_config = {"from_attributes": False}


class SpaceCreateBody(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str
    capacity: int = Field(gt=0)
    price_per_hour: float = Field(ge=0)


class SpaceUpdateBody(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    price_per_hour: float | None = Field(default=None, ge=0)
    min_duration_minutes: int | None = Field(default=None, gt=0)
    max_duration_minutes: int | None = Field(default=None, gt=0)
    min_advance_minutes: int | None = Field(default=None, ge=0)
    cancellation_deadline_hours: int | None = Field(default=None, ge=0)
    opening_time: time | None = None
    closing_time: time | None = None
    is_active: bool | None = None
