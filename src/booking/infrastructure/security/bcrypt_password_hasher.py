import asyncio
from functools import partial

from booking.infrastructure.security.password_crypto import (
    hash_password,
    verify_password,
)


class BcryptPasswordHasher:
    async def hash_password(self, plain_password: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(hash_password, plain_password))

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, partial(verify_password, plain_password, hashed_password)
        )
