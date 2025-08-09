import asyncio
import json
import logging
import os
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config
from utils import get_from_redis_with_retry, parse_config
from livekit.plugins import google as google_plugins


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    """ Entry point for the agent job """
    
    pid = os.getpid()
    logger.info(f"[pid={pid} job={ctx.job.id}] Starting Jarvis in room: {ctx.room.name}")

    await ctx.connect()

    # Try LiveKit metadata first
    agent_config = {}
    if ctx.room.metadata:
        try:
            agent_config = parse_config(ctx.room.metadata)
            logger.info(f"Using config from LiveKit metadata: {agent_config}")
        except json.JSONDecodeError:
            pass

    # Fallback to Redis if empty/missing
    if not agent_config:
        redis_key = f"Agent-Config:{ctx.room.name}"
        config_json = await get_from_redis_with_retry(redis_key)
        if config_json:
            agent_config = parse_config(config_json)
            logger.info(f"Using config from Redis: {config_json}")
        else:
            logger.warning(f"No agent config found in Redis for {ctx.room.name}, using defaults")

    # Fallback to defaults if still empty
    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    voice_cfg = agent_config.get("voice") or {}
    
    # Build TTS once
    tts = google_plugins.TTS(
        language=voice_cfg.get("language", config.DEFAULT_TTS_LANGUAGE),
        gender=voice_cfg.get("gender", config.DEFAULT_TTS_GENDER),
        voice_name=voice_cfg.get("voice_id", config.DEFAULT_TTS_VOICE),
        credentials_file=config.GOOGLE_APPLICATION_CREDENTIALS,
    )

    # Prewarm so first utterance uses correct voice
    try:
        tts.prewarm()
    except Exception:
        logger.exception("TTS prewarm failed")

    session = AgentSession(tts=tts)  # Apply at session level

    await session.start(
        agent=Assistant(model_id=model_id, tts=tts),
        room=ctx.room,
    )
