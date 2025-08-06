import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Starting Jarvis in room: {ctx.room.name}")
    
    await ctx.connect()
    session = AgentSession()
    
    await session.start(agent=Assistant(), room=ctx.room)
