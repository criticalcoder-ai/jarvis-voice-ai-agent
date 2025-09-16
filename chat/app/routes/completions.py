from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import uuid
import time

from app.schemas.completions import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionRequest,
    DeltaMessage,
)
from app.services.llm_client import llm_client
from app.services import chat_storage


router = APIRouter(tags=["completions"])


@router.post("/v1/chat/completions")
async def create_chat_completion(req: ChatCompletionRequest):
    """
    OpenAI-compatible endpoint for streaming chat completions with chat persistence.
    """
    run_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    chat_id = req.chat_id
    new_chat = chat_id is None
    if new_chat:
        chat_id = await chat_storage.create_chat(user_id=req.user)
        history_records = []
    else:
        history_records = await chat_storage.get_messages(chat_id)

    now = int(time.time())

    # Persist initial system/tool prompts for brand-new chats so future turns keep context.
    if new_chat:
        for message in req.messages:
            if message.role in ("system", "tool"):
                stored_message = {
                    "id": uuid.uuid4().hex,
                    "role": message.role,
                    "content": message.content,
                    "ts": now,
                }
                await chat_storage.append_message(chat_id, stored_message, dedupe=False)
                history_records.append(stored_message)

    # Persist the user's latest message (idempotent when message_id is reused).
    user_message = next((msg for msg in reversed(req.messages) if msg.role == "user"), None)
    user_message_id = req.message_id or uuid.uuid4().hex
    if user_message is not None:
        user_entry = {
            "id": user_message_id,
            "role": "user",
            "content": user_message.content,
            "ts": int(time.time()),
        }
        stored = await chat_storage.append_message(chat_id, user_entry, dedupe=True)
        if stored:
            history_records.append(user_entry)

    # Build context for the LLM with persisted history (fallback to request payload if empty).
    context_messages = [
        {"role": item["role"], "content": item["content"]}
        for item in history_records
    ]
    if not context_messages:
        context_messages = [m.model_dump() for m in req.messages]

    assistant_message_id = uuid.uuid4().hex
    assistant_tokens: list[str] = []

    async def event_stream():
        async for chunk in llm_client.stream_chat_completion(
            model=req.model,
            messages=context_messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            top_p=req.top_p,
            n=req.n,
            stop=req.stop,
        ):
            delta_role = getattr(chunk.choices[0].delta, "role", None)
            delta_content = getattr(chunk.choices[0].delta, "content", None)
            if delta_content:
                assistant_tokens.append(delta_content)

            choice = ChatCompletionChunkChoice(
                index=0,
                delta=DeltaMessage(
                    role=delta_role,
                    content=delta_content,
                ),
                finish_reason=chunk.choices[0].finish_reason,
            )
            out = ChatCompletionChunk(
                id=run_id,
                created=created,
                model=req.model,
                chat_id=chat_id,
                message_id=assistant_message_id,
                choices=[choice],
            )
            yield f"data: {out.model_dump_json()}\n\n"

        assistant_message = {
            "id": assistant_message_id,
            "role": "assistant",
            "content": "".join(assistant_tokens),
            "ts": int(time.time()),
        }
        await chat_storage.append_message(chat_id, assistant_message, dedupe=False)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
