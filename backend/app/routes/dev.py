import logging
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException, Query, status

from app.services.redis_client import redis_client


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dev", tags=["dev"])


async def _list_user_session_keys() -> List[str]:
    """Return all redis keys that match user_sessions:* safely.

    Tries KEYS first (simple for dev), falls back to iterative SCAN if not supported.
    """
    # Prefer KEYS for simplicity in dev tools
    try:
        keys = await redis_client.keys("user_sessions:*")
        if keys is None:
            return []
        # Upstash returns list[str]
        return keys  # type: ignore[return-value]
    except Exception as e:
        logger.debug(f"redis.keys not available, falling back to scan: {e}")

    # Fallback to SCAN iteration
    cursor = 0
    all_keys: List[str] = []
    try:
        while True:
            res = await redis_client.scan(cursor, match="user_sessions:*", count=1000)
            # Expect `(next_cursor, keys)`
            if isinstance(res, (list, tuple)) and len(res) == 2:
                cursor, batch = res
                if batch:
                    all_keys.extend(batch)
                if not cursor or int(cursor) == 0:
                    break
            else:
                # Unexpected shape; bail
                break
    except Exception as e:
        logger.exception(f"Failed to scan for session keys: {e}")
        return []

    return all_keys


@router.get("/sessions", status_code=status.HTTP_200_OK)
async def list_all_sessions() -> Dict[str, Any]:
    """List active sessions across all users (dev helper)."""
    keys = await _list_user_session_keys()
    users: List[Dict[str, Any]] = []
    total_sessions = 0

    for key in keys:
        try:
            sessions = await redis_client.smembers(key)  # type: ignore[arg-type]
            user_id = key.split(":", 1)[-1].replace("user_sessions:", "")
            # Some clients include full key; ensure only the part after prefix
            if user_id.startswith("user_sessions:"):
                user_id = user_id.split(":", 1)[-1]

            session_list = list(sessions or [])
            users.append({
                "user_id": user_id,
                "session_count": len(session_list),
                "sessions": session_list,
            })
            total_sessions += len(session_list)
        except Exception as e:
            logger.exception(f"Failed to fetch sessions for key {key}: {e}")

    return {"total_users": len(users), "total_sessions": total_sessions, "users": users}


@router.post("/redis/flush", status_code=status.HTTP_202_ACCEPTED)
async def flush_redis(confirm: bool = Query(False, description="Set to true to confirm flushing the entire Redis DB.")) -> Dict[str, str]:
    """Flush the entire Redis database (dev only). Requires confirm=true."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required: pass ?confirm=true to flush Redis")

    # Try native flush, fallback to deleting keys by pattern
    try:
        if hasattr(redis_client, "flushdb"):
            await redis_client.flushdb()  # type: ignore[attr-defined]
            logger.warning("Redis FLUSHDB executed via dev API")
            return {"status": "ok", "message": "Redis database flushed"}
    except Exception as e:
        logger.warning(f"flushdb not available or failed, falling back to delete by scan: {e}")

    # Fallback: iterate and delete keys (best-effort)
    deleted = 0
    try:
        # Prefer SCAN to avoid blocking
        cursor = 0
        while True:
            res = await redis_client.scan(cursor, match="*", count=1000)
            if isinstance(res, (list, tuple)) and len(res) == 2:
                cursor, keys = res
                if keys:
                    # Upstash supports UNLINK/DEL; use DEL for simplicity
                    await redis_client.delete(*keys)
                    deleted += len(keys)
                if not cursor or int(cursor) == 0:
                    break
            else:
                break
        logger.warning(f"Redis flushed by deleting {deleted} keys via dev API fallback")
        return {"status": "ok", "message": f"Deleted {deleted} keys"}
    except Exception as e:
        logger.exception(f"Failed to flush Redis by fallback method: {e}")
        raise HTTPException(status_code=500, detail="Failed to flush Redis")
