import json
import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Agent joining room: {ctx.room.name}")

    # Connect agent to the room 
    await ctx.connect()

    # Load config from room metadata or use defaults
    agent_config = {}
    if ctx.room.metadata:
        try:
            agent_config = json.loads(ctx.room.metadata)
        except json.JSONDecodeError:
            logger.warning("Room metadata is not valid JSON, using defaults")

    model_id = agent_config.get("model_id", config.DEFAULT_LLM_MODEL)
    voice = agent_config.get("voice", {})

    logger.info(f"Using config: {json.dumps(agent_config, indent=2)}")

    # Start the agent session
    session = AgentSession()
    await session.start(agent=Assistant(model_id=model_id, voice=voice), room=ctx.room)

    # Participant join handler
    async def on_participant_join(ctx: JobContext, participant):
        logger.info(f"Participant joined: {participant.identity}")


    # Register participant entrypoint callback (runs for each participant join)
    ctx.add_participant_entrypoint(on_participant_join)
