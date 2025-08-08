import asyncio
import json

from redis_client import redis_client


def parse_config(raw):
    if raw is None:
        return {}
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8", errors="replace")
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return {}

    # Handle the double-encoded case: obj is a JSON string
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except json.JSONDecodeError:
            return {}

    return obj if isinstance(obj, dict) else {}


async def get_from_redis_with_retry(key: str, attempts=2, delay=0):
    for i in range(attempts):
        raw = await redis_client.get(key)
        if raw:
            return raw
        if i < attempts - 1:
            await asyncio.sleep(delay)
    return None