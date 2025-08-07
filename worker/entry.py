import json
import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Starting Jarvis in room: {ctx.room.name}")

    # Extract metadata
    metadata = ctx.token.metadata or "{}"
    metadata_dict = json.loads(metadata)

    model_id = metadata_dict.get("model_id", config.DEFAULT_LLM_MODEL)
    voice_id = metadata_dict.get("voice_id", config.DEFAULT_TTS_VOICE)
    voice_gender = metadata_dict.get("voice_gender", "female")

    await ctx.connect()
    session = AgentSession()

    await session.start(
        agent=Assistant(
            model_id=model_id, voice_id=voice_id, voice_gender=voice_gender
        ),
        room=ctx.room,
    )
