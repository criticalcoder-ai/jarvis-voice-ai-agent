from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json, uuid, time

from app.schemas.completions import ChatCompletionChunk, ChatCompletionChunkChoice, ChatCompletionRequest, DeltaMessage
from app.services.llm_client import llm_client


router = APIRouter(tags=["completions"])


@router.post("/v1/chat/completions")
async def create_chat_completion(req: ChatCompletionRequest):
    """
    OpenAI-compatible endpoint for streaming chat completions.
    Always returns SSE with ChatCompletionChunk objects.
    """
    run_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    created = int(time.time())

    async def event_stream():
        async for chunk in llm_client.stream_chat_completion(
            model=req.model,
            messages=[m.model_dump() for m in req.messages],
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            top_p=req.top_p,
            n=req.n,
            stop=req.stop,
        ):
            # Convert upstream chunk into our Pydantic shape
            choice = ChatCompletionChunkChoice(
                index=0,
                delta=DeltaMessage(
                    role=getattr(chunk.choices[0].delta, "role", None),
                    content=getattr(chunk.choices[0].delta, "content", None),
                ),
                finish_reason=chunk.choices[0].finish_reason,
            )
            out = ChatCompletionChunk(
                id=run_id,
                created=created,
                model=req.model,
                choices=[choice],
            )
            yield f"data: {out.model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
