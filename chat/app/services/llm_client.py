import os
from openai import AsyncOpenAI
from typing import AsyncGenerator

from app import config

class LLMClient:
    """
    Wrapper around OpenAI-compatible API.
    Can point to OpenAI directly, or to a proxy like OpenRouter.
    """
    def __init__(self, base_url: str = None, api_key: str = None):
        self.client = AsyncOpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY
        )

    async def stream_chat_completion(self, **kwargs) -> AsyncGenerator[str, None]:
        """
        Streams assistant tokens from an LLM.

        Yields: partial chunks (as dicts) compatible with ChatCompletionChunk.
        """
        stream = await self.client.chat.completions.create(**kwargs, stream=True)
        async for event in stream:
            yield event

llm_client = LLMClient()