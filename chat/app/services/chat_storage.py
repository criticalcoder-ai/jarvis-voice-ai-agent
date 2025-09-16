import json
import time
import uuid
from typing import Any, Dict, List, Optional

from app.services.redis_client import redis_client


CHAT_KEY_PREFIX = "chat:"
CHAT_MESSAGES_SUFFIX = ":messages"


def _chat_key(chat_id: str) -> str:
    return f"{CHAT_KEY_PREFIX}{chat_id}"


def _chat_messages_key(chat_id: str) -> str:
    return f"{CHAT_KEY_PREFIX}{chat_id}{CHAT_MESSAGES_SUFFIX}"


async def create_chat(user_id: Optional[str] = None, title: Optional[str] = None) -> str:
    """Create a new chat record and return its ID."""
    chat_id = uuid.uuid4().hex
    now = int(time.time())
    metadata = {
        "created_at": str(now),
        "updated_at": str(now),
    }
    if user_id:
        metadata["user_id"] = user_id
    if title:
        metadata["title"] = title
    await redis_client.hset(_chat_key(chat_id), values=metadata)
    return chat_id


async def get_messages(chat_id: str) -> List[Dict[str, Any]]:
    """Return all messages stored for a chat."""
    raw_messages = await redis_client.lrange(_chat_messages_key(chat_id), 0, -1)
    messages: List[Dict[str, Any]] = []
    for raw in raw_messages or []:
        if raw is None:
            continue
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        messages.append(message)
    return messages


async def message_exists(chat_id: str, message_id: Optional[str]) -> bool:
    if not message_id:
        return False
    existing = await get_messages(chat_id)
    return any(msg.get("id") == message_id for msg in existing)


async def append_message(
    chat_id: str,
    message: Dict[str, Any],
    *,
    dedupe: bool = True,
) -> bool:
    """
    Persist a chat message. Returns True if stored, False if skipped due to dedupe.
    """
    message_id = message.get("id")
    if dedupe and await message_exists(chat_id, message_id):
        return False

    payload = json.dumps(message)
    await redis_client.rpush(_chat_messages_key(chat_id), payload)
    updates = {
        "updated_at": str(int(time.time())),
    }
    if message_id:
        updates["last_message_id"] = message_id
    await redis_client.hset(_chat_key(chat_id), values=updates)
    return True
