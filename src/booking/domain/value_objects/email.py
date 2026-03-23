import re
from dataclasses import dataclass

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if not EMAIL_REGEX.match(self.value):
            raise ValueError(f"Invalid email address: {self.value}")

    def __str__(self) -> str:
        return self.value
