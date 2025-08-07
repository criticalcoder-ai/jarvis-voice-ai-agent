import logging

from app.services.redis_client import redis_client 

logger = logging.getLogger(__name__)

# Key patterns
BLACKLIST_KEY = "blacklist:{token}"
USER_SESSIONS_KEY = "user_sessions:{user_id}"


async def blacklist_token(token: str, expire_seconds: int):
    """
    Blacklist a JWT token so it cannot be reused.

    Args:
        token (str): The JWT token string
        expire_seconds (int): Expiration time in seconds (usually token's own lifetime)
    """
    try:
        key = BLACKLIST_KEY.format(token=token)
        await redis_client.set(key, "1", ex=expire_seconds)
        logger.info(f"Token blacklisted for {expire_seconds}s: {token[:10]}...")
    except Exception as e:
        logger.exception(f"Failed to blacklist token: {e}")


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.

    Args:
        token (str): The JWT token string

    Returns:
        bool: True if token is blacklisted, False otherwise
    """
    try:
        key = BLACKLIST_KEY.format(token=token)
        return await redis_client.exists(key) == 1
    except Exception as e:
        logger.exception(f"Failed to check token blacklist: {e}")
        return False


