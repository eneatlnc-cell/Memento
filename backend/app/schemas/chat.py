"""Chat-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single chat message."""

    role: str = Field(..., pattern="^(user|assistant|system|tool)$")
    content: str | None = None
    name: str | None = None
    tool_calls: list[dict] | None = None
    tool_call_id: str | None = None


class ChatRequest(BaseModel):
    """Request body for chat completion."""

    messages: list[ChatMessage] = Field(..., min_length=1, max_length=100)
    model: str = Field(default="agnes-chat-v1")
    stream: bool = True
    provider_id: str | None = Field(default=None)


class ChatHistoryResponse(BaseModel):
    """Chat history record."""

    id: str
    user_id: str
    title: str
    messages: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}