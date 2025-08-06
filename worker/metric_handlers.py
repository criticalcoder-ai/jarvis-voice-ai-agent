import logging

logger = logging.getLogger(__name__)

async def handle_llm_metrics(metrics):
    logger.info("\n--- LLM Metrics ---")
    logger.info(f"Prompt Tokens: {metrics.prompt_tokens}")
    logger.info(f"Completion Tokens: {metrics.completion_tokens}")
    logger.info(f"Tokens per second: {metrics.tokens_per_second:.4f}")
    logger.info(f"TTFT: {metrics.ttft:.4f}s")
    logger.info("------------------\n")

async def handle_stt_metrics(metrics):
    logger.info("\n--- STT Metrics ---")
    logger.info(f"Duration: {metrics.duration:.4f}s")
    logger.info(f"Audio Duration: {metrics.audio_duration:.4f}s")
    logger.info(f"Streamed: {'Yes' if metrics.streamed else 'No'}")
    logger.info("------------------\n")

async def handle_eou_metrics(metrics):
    logger.info("\n--- End of Utterance Metrics ---")
    logger.info(f"End of Utterance Delay: {metrics.end_of_utterance_delay:.4f}s")
    logger.info(f"Transcription Delay: {metrics.transcription_delay:.4f}s")
    logger.info("--------------------------------\n")

async def handle_tts_metrics(metrics):
    logger.info("\n--- TTS Metrics ---")
    logger.info(f"TTFB: {metrics.ttfb:.4f}s")
    logger.info(f"Duration: {metrics.duration:.4f}s")
    logger.info(f"Audio Duration: {metrics.audio_duration:.4f}s")
    logger.info(f"Streamed: {'Yes' if metrics.streamed else 'No'}")
    logger.info("------------------\n")
