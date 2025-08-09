import json
import logging
import os
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config
from utils import parse_config
from redis_client import redis_client
from livekit.agents import AgentSession, JobContext

logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    pid = os.getpid()
    logger.info(f"[pid={pid} job={ctx.job.id}] Starting Jarvis in room: {ctx.room.name}")

    await ctx.connect()

    # === Get config: prefer metadata, fallback to Redis (no retry) ===
    agent_config = {}
    if ctx.room.metadata:
        try:
            agent_config = parse_config(ctx.room.metadata) or {}
            logger.info("Using config from LiveKit metadata: %s", agent_config)
        except json.JSONDecodeError:
            pass

    if not agent_config:
        redis_key = f"agent_config:{ctx.room.name}"  # normalize the key
        raw = await redis_client.get(redis_key)
        if raw:
            agent_config = parse_config(raw) or {}
            logger.info("Using config from Redis (parsed).")
        else:
            logger.warning("No agent config found; using defaults")

    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    v = agent_config.get("voice") or {}
    voice_name = v.get("voice_id", config.DEFAULT_TTS_VOICE)
    language   = v.get("language",  config.DEFAULT_TTS_LANGUAGE)
    gender     = v.get("gender",    config.DEFAULT_TTS_GENDER)

    # === Create session first (no start yet) ===
    session = AgentSession()

    # === FORCE the TTS on the session BEFORE start() ===
    # Different LiveKit Agents versions expose different methods; try both.
    if hasattr(session, "update_tts"):
        await session.update_tts(
            provider="google",
            voice=voice_name,
            languageCode=language,
            gender=gender,
        )
    elif hasattr(session, "set_voice"):
        await session.set_voice({
            "provider": "google",
            "voice": voice_name,
            "languageCode": language,
            "gender": gender,
        })
    else:
        logger.warning("Session has no update_tts/set_voice; consider passing a TTS object to AgentSession(tts=...)")

    # === Prime the synth so the very first render uses THIS voice ===
    try:
        # Tiny SSML “tickle”—fast, inaudible, but forces the graph to lock the new voice
        await session.say('<speak><break time="10ms"/></speak>', ssml=True)
    except Exception:
        # Some builds won’t allow say() before start(); that’s fine—we still forced update_tts above.
        pass

    # === Now start the agent ===
    await session.start(
        agent=Assistant(model_id=model_id, voice=v),  # keep your current Assistant signature
        room=ctx.room,
    )
