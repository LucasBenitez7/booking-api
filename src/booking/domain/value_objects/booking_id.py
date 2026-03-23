import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class BookingId:
    value: uuid.UUID

    @classmethod
    def generate(cls) -> "BookingId":
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, value: str) -> "BookingId":
        return cls(value=uuid.UUID(value))

    def __str__(self) -> str:
        return str(self.value)
