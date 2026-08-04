"""Chat routes with SSE streaming."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.chat import ChatRequest
from app.services.chat_service import chat_stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("")
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """AI chat endpoint with SSE streaming."""
    messages = [msg.model_dump(exclude_none=True) for msg in body.messages]

    return StreamingResponse(
        chat_stream(
            messages=messages,
            model=body.model,
            provider_id=body.provider_id or "",
            user_id=current_user.id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )