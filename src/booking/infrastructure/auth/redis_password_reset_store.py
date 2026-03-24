import redis.asyncio as redis


class RedisPasswordResetStore:
    def __init__(self, client: redis.Redis) -> None:
        self._redis = client

    async def store(self, token: str, user_id: str, ttl_seconds: int) -> None:
        key = f"pwdreset:{token}"
        await self._redis.setex(key, ttl_seconds, user_id)

    async def consume(self, token: str) -> str | None:
        key = f"pwdreset:{token}"
        async with self._redis.pipeline(transaction=True) as pipe:
            await pipe.get(key)
            await pipe.delete(key)
            results = await pipe.execute()
        raw = results[0]
        if raw is None:
            return None
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)
