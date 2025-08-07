import os
from upstash_redis.asyncio import redis


redis_client = redis.from_url(
    os.getenv("UPSTASH_REDIS_URL"),
    decode_responses=True
)
