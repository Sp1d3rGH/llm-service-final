import redis.asyncio as aioredis

from app.core.config import settings

redis_client = aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)


def get_redis() -> aioredis.Redis:
    """
    Возвращает настроенный асинхронный клиент Redis.
    """
    return redis_client
