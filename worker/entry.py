import asyncio
import json
import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Starting Jarvis in room: {ctx.room.name}")


    await ctx.connect()

    # Get agent config from room metadata
    agent_config = {}
    if ctx.room.metadata:
        raw = ctx.room.metadata
        agent_config = json.loads(raw)
        

    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    voice = agent_config.get("voice", {})

    print("-"*20)
    logger.info(f"Using config: {json.dumps(agent_config, indent=2)}")
    print("-"*20)

    
    session = AgentSession()
    
    await session.start(
        agent=Assistant(model_id=model_id, voice=voice),
        room=ctx.room,
    )
