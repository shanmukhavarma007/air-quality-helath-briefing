import json
import redis.asyncio as aioredis
from loguru import logger
from app.config import settings


class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def get(self, key: str) -> dict | None:
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None

    async def set(self, key: str, value: dict, ttl: int = 300) -> None:
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def close(self):
        await self.redis.close()
