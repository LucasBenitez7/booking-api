"""In-process token store for tests or environments without Redis.

Tokens expire based on wall-clock time so TTL is honoured even without Redis.
"""

import time


class MemoryPasswordResetStore:
    def __init__(self) -> None:
        self._tokens: dict[str, tuple[str, float]] = {}  # token -> (user_id, expires_at)

    async def store(self, token: str, user_id: str, ttl_seconds: int) -> None:
        self._tokens[token] = (user_id, time.monotonic() + ttl_seconds)

    async def consume(self, token: str) -> str | None:
        entry = self._tokens.get(token)
        if entry is None:
            return None
        user_id, expires_at = entry
        del self._tokens[token]
        if time.monotonic() > expires_at:
            return None
        return user_id
