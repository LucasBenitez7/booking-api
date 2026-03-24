from typing import Protocol


class PasswordResetTokenStore(Protocol):
    """Opaque token storage for password reset (Redis-backed in production)."""

    async def store(self, token: str, user_id: str, ttl_seconds: int) -> None: ...

    async def consume(self, token: str) -> str | None:
        """Return user_id if token is valid, then invalidate it. Single-use."""
