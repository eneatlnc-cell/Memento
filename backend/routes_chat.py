"""Chat route — SSE streaming, no auth, no DB."""
from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend import agnes

router = APIRouter(prefix="/api", tags=["Chat"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = "agnes-2.5-flash"


@router.post("/chat")
async def chat(body: ChatRequest) -> Any:
    """AI chat with SSE streaming. Passes messages straight to Agnes."""
    messages = [m.model_dump() for m in body.messages]

    async def event_stream():
        try:
            async for chunk in agnes.chat_stream(messages, body.model):
                yield chunk
        except httpx.HTTPStatusError as exc:
            yield _err(f"Upstream error: {exc}")
        except RuntimeError as exc:
            yield _err(str(exc))
        except Exception as exc:  # noqa: BLE001
            yield _err(f"Unexpected error: {exc}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _err(msg: str) -> str:
    return f"data: {json.dumps({'error': msg})}\n\n"
