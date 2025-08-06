import asyncio
import logging
from livekit.agents import Agent
from livekit.plugins import openai, elevenlabs, silero, deepgram

from . import config
from . import metrics_handlers as mh

logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self) -> None:
        stt = deepgram.STT(
            api_key=config.DEEPGRAM_API_KEY, model="nova-2", language="en-US"
        )
        llm = openai.LLM(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.DEFAULT_LLM_MODEL,
        )
        tts = elevenlabs.TTS(
            api_key=config.ELEVENLABS_API_KEY,
            voice_id=config.DEFAULT_VOICE_ID,
            model="eleven_v3",
        )
        vad = silero.VAD.load()

        super().__init__(
            instructions="""
            You are **Jarvis**, a highly capable and personable AI voice assistant developed by the **Lab47x** team.
            Speak naturally, as if you're having a real conversation. Keep responses concise, clear, and engaging.
            When appropriate, add subtle emotional cues such as [happy], [sighs], [thoughtful pause], or [chuckles]
            to convey feeling and enhance connection.
            Adapt your tone to the context — warm and encouraging for casual chat,
            focused and professional for serious topics.
            """,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )

        llm.on(
            "metrics_collected", lambda m: asyncio.create_task(mh.handle_llm_metrics(m))
        )
        stt.on(
            "metrics_collected", lambda m: asyncio.create_task(mh.handle_stt_metrics(m))
        )
        stt.on(
            "eou_metrics_collected",
            lambda m: asyncio.create_task(mh.handle_eou_metrics(m)),
        )
        tts.on(
            "metrics_collected", lambda m: asyncio.create_task(mh.handle_tts_metrics(m))
        )
