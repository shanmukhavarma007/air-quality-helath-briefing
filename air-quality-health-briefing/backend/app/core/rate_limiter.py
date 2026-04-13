import redis.asyncio as aioredis
from datetime import datetime, timezone
from loguru import logger

DAILY_AI_QUOTA = 50


async def check_and_increment_ai_quota(redis_client: aioredis.Redis) -> tuple[bool, int]:
    now = datetime.now(timezone.utc)
    quota_key = f"ai_quota:{now.strftime('%Y-%m-%d')}"

    current = await redis_client.incr(quota_key)

    if current == 1:
        seconds_until_midnight = 86400 - now.hour * 3600 - now.minute * 60 - now.second
        await redis_client.expire(quota_key, seconds_until_midnight)
        logger.info(f"AI quota counter initialized for {now.date()}")

    if current > DAILY_AI_QUOTA:
        await redis_client.decr(quota_key)
        logger.warning(f"AI quota exhausted for {now.date()} — request denied")
        return False, DAILY_AI_QUOTA

    logger.info(f"AI quota: {current}/{DAILY_AI_QUOTA} used today")
    return True, current


async def get_ai_quota_remaining(redis_client: aioredis.Redis) -> int:
    now = datetime.now(timezone.utc)
    quota_key = f"ai_quota:{now.strftime('%Y-%m-%d')}"
    used = await redis_client.get(quota_key)
    used = int(used) if used else 0
    return max(0, DAILY_AI_QUOTA - used)
