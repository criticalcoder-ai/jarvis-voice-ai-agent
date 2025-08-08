import asyncio
import json
import logging
import os
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config
from redis_client import redis_client


logger = logging.getLogger(__name__)




async def entry_point(ctx: JobContext):
    pid = os.getpid()
    logger.info(f"[pid={pid} job={ctx.job.id}] Starting Jarvis in room: {ctx.room.name}")

    if getattr(ctx, "_agent_started", False):
        logger.info("agent already started in this ctx; skipping")
        return

    await ctx.connect()

    # Try LiveKit metadata first
    agent_config = {}
    if ctx.room.metadata:
        try:
            agent_config = json.loads(ctx.room.metadata)
            logger.info(f"Using config from LiveKit metadata: {agent_config}")
        except json.JSONDecodeError:
            pass

    # Fallback to Redis if empty/missing
    if not agent_config:
        redis_key = f"Agent Config:{ctx.room.name}"
        config_json = await redis_client.get(redis_key)
        if config_json:
            agent_config = json.loads(config_json)
            logger.info(f"Using config from Redis: {config_json}")
        else:
            logger.warning(f"No agent config found in Redis for {ctx.room.name}, using defaults")


    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    voice = agent_config.get("voice", {})

    

    session = AgentSession()

    await session.start(
        agent=Assistant(model_id=model_id, voice=voice),
        room=ctx.room,
    )
