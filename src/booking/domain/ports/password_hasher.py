from typing import Protocol


class PasswordHasher(Protocol):
    async def hash_password(self, plain_password: str) -> str: ...

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...
