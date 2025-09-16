from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Dict


class ChatMessage(BaseModel):
    """
    Represents a single message in a chat completion request.
    """

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="Role of the message author"
    )
    content: Union[str, List[Dict]] = Field(
        ..., description="Message content as plain text or structured objects"
    )


class ChatCompletionRequest(BaseModel):
    """
    OpenAI-compatible request model for starting a chat completion run.
    """

    model: str = Field(..., description="ID of the model to use (e.g., gpt-4o-mini)")
    messages: List[ChatMessage] = Field(..., description="Conversation history so far")
    temperature: Optional[float] = Field(
        1.0, description="Sampling temperature (higher = more random)"
    )
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stop: Optional[Union[str, List[str]]] = Field(
        None, description="Stop sequence(s) where generation should end"
    )
    top_p: Optional[float] = Field(
        1.0, description="Nucleus sampling (alternative to temperature)"
    )
    n: Optional[int] = Field(1, description="Number of completions to generate")
    user: Optional[str] = Field(
        None,
        description="Unique identifier for the end-user (for logging/abuse monitoring)",
    )
    chat_id: Optional[str] = Field(
        None,
        description="Existing chat thread ID. If omitted, a new chat is created.",
    )
    message_id: Optional[str] = Field(
        None,
        description="Client-supplied ID for the new user message (for idempotency).",
    )


class DeltaMessage(BaseModel):
    """
    Represents the incremental content of the assistant's reply
    during a streamed chat completion.

    - The first chunk may include a `role="assistant"`.
    - Subsequent chunks usually contain partial `content` tokens.
    - The final chunk has an empty delta and a finish_reason.
    """

    role: Optional[str] = Field(
        None, description="Role of the message (usually only in the first chunk)."
    )
    content: Optional[str] = Field(
        None, description="Partial content tokens emitted by the model."
    )


class ChatCompletionChunkChoice(BaseModel):
    """
    A single streaming choice inside a completion chunk.

    - index: which choice this belongs to (default 0 if n=1).
    - delta: incremental update to the assistant's message.
    - finish_reason: 'stop', 'length', or None if still streaming.
    """

    index: int = Field(..., description="Index of the choice (0 if single choice).")
    delta: DeltaMessage = Field(
        ..., description="Incremental content (role or text tokens)."
    )
    finish_reason: Optional[str] = Field(
        None, description="Reason generation finished (stop, length, tool, etc.)."
    )


class ChatCompletionChunk(BaseModel):
    """
    OpenAI-compatible streamed response chunk.

    Each chunk is sent as a Server-Sent Event (SSE) with 'data: ...'.
    Clients receive multiple chunks until a '[DONE]' marker is sent.
    """

    id: str = Field(..., description="Unique ID for the chat completion run.")
    object: str = Field(
        default="chat.completion.chunk",
        description="Response object type (always 'chat.completion.chunk').",
    )
    created: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp()),
        description="Unix timestamp (seconds) when the chunk was created.",
    )
    model: str = Field(..., description="The model that generated this chunk.")
    chat_id: Optional[str] = Field(
        None, description="Chat thread ID for stateful conversations."
    )
    message_id: Optional[str] = Field(
        None, description="Identifier for the assistant message being streamed."
    )
    choices: List[ChatCompletionChunkChoice] = Field(
        ..., description="List of choices being streamed (usually length 1)."
    )
