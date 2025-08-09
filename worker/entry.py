import json
import logging
import os
from typing import Dict, Any, Tuple

from livekit.agents import AgentSession, JobContext
from livekit.plugins.google import TTS as GoogleTTS

from agent import Assistant
import config
from utils import parse_config
from redis_client import redis_client  # simple, single GET fallback

logger = logging.getLogger(__name__)


_TTS_CACHE: dict[Tuple[str, str, str], GoogleTTS] = {}


def _get_tts(voice_cfg: Dict[str, Any]) -> GoogleTTS:
    voice_id = (voice_cfg.get("voice_id") or config.DEFAULT_TTS_VOICE or "").strip()
    language = (voice_cfg.get("language") or config.DEFAULT_TTS_LANGUAGE or "").strip()
    gender   = (voice_cfg.get("gender")   or config.DEFAULT_TTS_GENDER   or "").strip()

    key = (voice_id, language, gender)
    tts = _TTS_CACHE.get(key)
    if tts is None:
        tts = GoogleTTS(
            language=language,
            gender=gender,
            voice_name=voice_id,
            credentials_file=config.GOOGLE_APPLICATION_CREDENTIALS,
        )
        try:
            tts.prewarm()  # ensure first utterance uses the selected voice
            logger.info("Prewarmed TTS (voice=%s lang=%s gender=%s)", voice_id, language, gender)
        except Exception:
            logger.exception("TTS prewarm failed (continuing)")

        _TTS_CACHE[key] = tts

    return tts


async def entry_point(ctx: JobContext):
    """Entry point for the agent job."""
    pid = os.getpid()
    logger.info("[pid=%s job=%s] Starting Jarvis in room: %s", pid, ctx.job.id, ctx.room.name)

    # Connect to room first
    await ctx.connect()

    # Prefer LiveKit metadata
    agent_config: Dict[str, Any] = {}
    if ctx.room.metadata:
        agent_config = parse_config(ctx.room.metadata) or {}
        if agent_config:
            logger.info("Using config from LiveKit metadata: %s", agent_config)

    # Fallback: single Redis GET 
    if not agent_config:
        redis_key = f"agent_config:{ctx.room.name}"
        raw = await redis_client.get(redis_key)
        if raw:
            agent_config = parse_config(raw) or {}
            if agent_config:
                logger.info("Using config from Redis (parsed).")
            else:
                logger.warning("Redis value present but not valid JSON for key=%s", redis_key)
        else:
            logger.warning("No agent config found in Redis for %s; using defaults.", ctx.room.name)

    # Defaults if still empty
    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    voice_cfg = agent_config.get("voice") or {}


    # Build (or reuse) prewarmed TTS and give it to the session BEFORE start
    tts = _get_tts(voice_cfg)
    session = AgentSession(tts=tts)

    # Start with a single source of truth for TTS (no separate voice dicts)
    await session.start(
        agent=Assistant(model_id=model_id, tts=tts),
        room=ctx.room,
    )
