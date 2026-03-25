from datetime import datetime, time

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from booking.infrastructure.persistence.database import Base


class SpaceModel(Base):
    __tablename__ = "spaces"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_hour: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    max_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=480, nullable=False
    )
    min_advance_minutes: Mapped[int] = mapped_column(
        Integer, default=60, nullable=False
    )
    cancellation_deadline_hours: Mapped[int] = mapped_column(
        Integer, default=24, nullable=False
    )
    opening_time: Mapped[time] = mapped_column(Time, default=time(8, 0), nullable=False)
    closing_time: Mapped[time] = mapped_column(
        Time, default=time(22, 0), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
