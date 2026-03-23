from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("TimeSlot datetimes must be timezone-aware")
        if self.start >= self.end:
            raise ValueError("Start datetime must be before end datetime")
        if self.start < datetime.now(tz=UTC):
            raise ValueError("TimeSlot cannot start in the past")

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.start < other.end and self.end > other.start

    def duration_minutes(self) -> float:
        return (self.end - self.start).total_seconds() / 60

    def __str__(self) -> str:
        return f"{self.start.isoformat()} → {self.end.isoformat()}"
