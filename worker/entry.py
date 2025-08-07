import json
import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Starting Jarvis in room: {ctx.room.name}")

    # Get metadata from agent
    # metadata = ctx.job.metadata  # JSON string

    # metadata_dict = json.loads(metadata)
    metadata_dict = {}

    model_id = metadata_dict.get("model_id", config.DEFAULT_LLM_MODEL)
    voice_id = metadata_dict.get("voice_id", config.DEFAULT_TTS_VOICE)
    voice_gender = metadata_dict.get("voice_gender", "female")

    logger.info(f"Model ID: {model_id}")
    logger.info(f"Voice ID: {voice_id}")
    logger.info(f"Voice Gender: {voice_gender}")


    await ctx.connect()
    session = AgentSession()

    await session.start(
        agent=Assistant(
            model_id=model_id, voice_id=voice_id, voice_gender=voice_gender
        ),
        room=ctx.room,
    )
