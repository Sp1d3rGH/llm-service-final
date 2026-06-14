"""
Клиент Redis для Bot Service.
Предоставляет единую точку получения асинхронного клиента.
"""

import redis.asyncio as aioredis

from app.core.config import settings

# Создаём клиент один раз на уровне модуля
redis_client = aioredis.from_url(str(settings.REDIS_URL), decode_responses=True)


def get_redis() -> aioredis.Redis:
    """Возвращает настроенный асинхронный клиент Redis."""
    return redis_client