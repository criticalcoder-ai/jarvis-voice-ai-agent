from upstash_redis.asyncio import Redis
import app.config as config

redis_client = Redis(
    url=config.UPSTASH_REDIS_REST_URL, token=config.UPSTASH_REDIS_REST_TOKEN
)
