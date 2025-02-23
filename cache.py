import asyncio
from typing import Optional
import redis.asyncio as redis
from config import settings
from fastapi import Depends, HTTPException

async def get_redis_client() -> redis.Redis:
    """Create a Redis client for caching."""
    try:
        # Only include password if explicitly set
        kwargs = {
            "host": settings.REDIS_HOST,
            "port": settings.REDIS_PORT,
            "db": settings.REDIS_DB,
            "decode_responses": True,
        }
        if settings.REDIS_PASSWORD is not None:
            kwargs["password"] = settings.REDIS_PASSWORD

        client = redis.Redis(**kwargs)
        await client.ping()  # Test connection
        return client
    except redis.AuthenticationError:
        raise HTTPException(status_code=503, detail="Redis authentication failed. Check REDIS_PASSWORD configuration.")
    except redis.ConnectionError:
        raise HTTPException(status_code=503, detail="Failed to connect to Redis. Check host and port settings.")

async def get_cache(key: str, redis_client: redis.Redis = Depends(get_redis_client)) -> Optional[str]:
    """Retrieve a value from Redis cache."""
    try:
        return await redis_client.get(key)
    except redis.RedisError:
        return None

async def set_cache(key: str, value: str, ttl: int = 3600, redis_client: redis.Redis = Depends(get_redis_client)):
    """Set a value in Redis cache with a TTL (default 1 hour)."""
    try:
        await redis_client.setex(key, ttl, value)
    except redis.RedisError:
        pass  # Silently fail if cache set fails
    

asyncio.run(get_redis_client())