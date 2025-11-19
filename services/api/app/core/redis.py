"""Redis connection and client."""

import redis.asyncio as aioredis
from redis import Redis
from typing import Optional
from app.config import settings

# Sync Redis client
redis_client: Optional[Redis] = None

# Async Redis client
async_redis_client: Optional[aioredis.Redis] = None


def get_redis() -> Redis:
    """Get synchronous Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=settings.redis_pool_size
        )
    return redis_client


async def get_async_redis() -> aioredis.Redis:
    """Get asynchronous Redis client."""
    global async_redis_client
    if async_redis_client is None:
        async_redis_client = await aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=settings.redis_pool_size
        )
    return async_redis_client


async def close_redis():
    """Close Redis connections."""
    global redis_client, async_redis_client
    if redis_client:
        redis_client.close()
    if async_redis_client:
        await async_redis_client.close()

