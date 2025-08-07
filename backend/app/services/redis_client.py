import os
from upstash_redis.asyncio import Redis


redis_client = Redis.from_url(
    os.getenv("UPSTASH_REDIS_URL"),
    decode_responses=True
)
