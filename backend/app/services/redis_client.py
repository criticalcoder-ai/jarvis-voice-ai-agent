from upstash_redis.asyncio import Redis
import app.config as config

redis_client = Redis(url=config.REDIS_URL, token=config.REDIS_TOKEN)
