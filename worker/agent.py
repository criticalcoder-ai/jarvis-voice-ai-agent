import asyncio
import json
import logging
import config
import metric_handlers as mh
from livekit.agents import Agent
from livekit.plugins import openai, silero, deepgram, google


logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self, model_id: str, voice: dict) -> None:
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

        tts = google.TTS(
            language=voice.get("language", config.DEFAULT_TTS_LANGUAGE),
            gender=voice.get("gender", config.DEFAULT_TTS_GENDER),
            voice_name=voice.get("voice_id", config.DEFAULT_TTS_VOICE),
            credentials_file=config.GOOGLE_APPLICATION_CREDENTIALS,
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
