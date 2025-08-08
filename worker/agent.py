import asyncio
import json
import logging
import config
import metric_handlers as mh
from livekit.agents import Agent
from livekit.plugins.google import TTS as GoogleTTS
from livekit.plugins import openai, silero, deepgram


logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self, model_id: str, tts: GoogleTTS) -> None:
        stt = deepgram.STT(
            api_key=config.DEEPGRAM_API_KEY,
            model=config.DEFAULT_STT_MODEL,
            language=config.DEFAULT_STT_LANGUAGE,
        )

        llm = openai.LLM(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=model_id,
        )

        vad = silero.VAD.load()

        super().__init__(
            instructions=config.AGENT_INSTRUCTIONS,
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )

        # # Attach metrics listeners
        # llm.on(
        #     "metrics_collected", lambda m: asyncio.create_task(mh.handle_llm_metrics(m))
        # )
        # stt.on(
        #     "metrics_collected", lambda m: asyncio.create_task(mh.handle_stt_metrics(m))
        # )
        # stt.on(
        #     "eou_metrics_collected",
        #     lambda m: asyncio.create_task(mh.handle_eou_metrics(m)),
        # )
        # tts.on(
        #     "metrics_collected", lambda m: asyncio.create_task(mh.handle_tts_metrics(m))
        # )
