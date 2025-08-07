import asyncio
import json
import logging
from livekit.agents import AgentSession, JobContext
from agent import Assistant
import config


logger = logging.getLogger(__name__)


async def entry_point(ctx: JobContext):
    logger.info(f"Starting Jarvis in room: {ctx.room.name}")

    # Connect first (agent becomes a room participant)
    await ctx.connect()


    # Wait for a participant (user) to join so we can read token metadata.
    # Use a small timeout to avoid hanging forever.
    participant_meta = {}
    try:
        participant = await asyncio.wait_for(ctx.wait_for_participant(), timeout=60)
        raw = participant.metadata or "{}"
        try:
            participant_meta = json.loads(raw)
        except Exception:
            logger.warning("Participant metadata is not valid JSON; ignoring.")
    except asyncio.TimeoutError:
        logger.info("No participant joined within 15s; using defaults/job metadata.")

    metadata = participant_meta

    model_id = metadata.get("model_id", config.DEFAULT_LLM_MODEL)
    voice_id = metadata.get("voice_id", config.DEFAULT_TTS_VOICE)
    voice_gender = metadata.get("voice_gender", "male")

    logger.info(f"Model ID: {model_id} | Voice ID: {voice_id} | Voice Gender: {voice_gender}")

    session = AgentSession()
    
    await session.start(
        agent=Assistant(model_id=model_id, voice_id=voice_id, voice_gender=voice_gender),
        room=ctx.room,
    )
