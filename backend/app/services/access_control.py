# app/services/access_control.py
import hashlib
from datetime import datetime
from typing import Optional
import logging
from app.schemas.access_control import AccessResult, TierLimits
from app.services.exceptions import LimitExceededError, TierNotFoundError
from app.services.redis_client import redis_client

logger = logging.getLogger(__name__)


class AccessControlService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.tiers = {
            "guest": TierLimits(
                name="Guest",
                session_duration=120,  # 2 minutes
                concurrent_sessions=1,
                daily_limit=2,  # 2 min/day
                features=["basic_voice_chat"],
            ),
            "free": TierLimits(
                name="Free",
                session_duration=None,  # Unlimited per session
                concurrent_sessions=2,
                daily_limit=120,  # 120 min/day
                features=["voice_chat", "long_sessions"],
            ),
        }

    async def get_active_sessions(self, user_id: str) -> int:
        """Returns the number of active sessions for a user."""
        return await self.redis.scard(f"user_sessions:{user_id}") or 0

    async def _get_daily_usage(self, user_id: str) -> int:
        """Returns the number of minutes used today for the user."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return int(await self.redis.get(f"user_daily_usage:{user_id}:{today}") or 0)

    async def check_permission(self, user_id: str, tier: str) -> AccessResult:
        """Checks if a user has permission to access a given tier."""
        if tier not in self.tiers:
            logger.warning(f"Tier '{tier}' not found for user {user_id}")
            raise TierNotFoundError(f"Invalid tier: {tier}")

        limits = self.tiers[tier]

        # Concurrent session check
        active_count = await self.get_active_sessions(user_id)
        if active_count >= limits.concurrent_sessions:
            raise LimitExceededError("Concurrent session limit reached")

        # Daily usage check
        usage = await self._get_daily_usage(user_id)
        if limits.daily_limit is not None and usage >= limits.daily_limit:
            raise LimitExceededError("Daily usage limit reached")

        return AccessResult(allowed=True)

    async def start_session(self, user_id: str, session_id: str):
        """
        Marks a new session as active for the user in Redis.

        Redis Structure:
            user_sessions:{user_id} = SET of active session IDs
        """

        await self.redis.sadd(f"user_sessions:{user_id}", session_id)

        # Expire the session after the specified duration
        await self.redis.expire(f"user_sessions:{user_id}", 3600)

    async def end_session(self, user_id: str, session_id: str, duration_seconds: int):
        """
        Ends a user's active session and updates their daily usage counter.

        Redis Structures:
            user_sessions:{user_id}               = SET of active session IDs
            user_daily_usage:{user_id}:{YYYY-MM-DD} = Integer (minutes used today)
        """

        await self.redis.srem(f"user_sessions:{user_id}", session_id)

        # Get today's date for per-day usage tracking
        today = datetime.utcnow().strftime("%Y-%m-%d")
        usage_key = f"user_daily_usage:{user_id}:{today}"

        # Increment usage counter by the number of minutes in this session
        await self.redis.incrby(usage_key, duration_seconds // 60)

        # Set the daily usage key to expire in 24 hours
        # Resets the user's daily usage at the start of a new day
        await self.redis.expire(usage_key, 86400)


access_control = AccessControlService(redis_client=redis_client)