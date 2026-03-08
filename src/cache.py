import redis
import os
import logging

logger = logging.getLogger(__name__)

VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", "6379"))
CACHE_TTL = 300  # 5 minutes in seconds


def get_valkey_client():
    return redis.Redis(
        host=VALKEY_HOST,
        port=VALKEY_PORT,
        decode_responses=True
    )


def get_cached_temperature():
    try:
        client = get_valkey_client()
        data = client.get("temperature_data")
        if data:
            logger.info("Cache hit — returning cached temperature")
            return data
        logger.info("Cache miss — no data in cache")
        return None
    except redis.RedisError as e:
        logger.error("Cache read failed: %s", e)
        return None


def set_cached_temperature(data: str):
    try:
        client = get_valkey_client()
        client.setex("temperature_data", CACHE_TTL, data)
        logger.info("Temperature data cached for %s seconds", CACHE_TTL)
    except redis.RedisError as e:
        logger.error("Cache write failed: %s", e)


def is_cache_fresh():
    try:
        client = get_valkey_client()
        ttl = client.ttl("temperature_data")
        # ttl > 0 means key exists and has expiry
        # ttl == -1 means key exists but no expiry
        # ttl == -2 means key doesn't exist
        return ttl > 0
    except redis.RedisError as e:
        logger.error("Cache TTL check failed: %s", e)
        return False