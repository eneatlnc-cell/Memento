"""Chat service with SSE streaming and tool calling support."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import async_session_factory
from backend.models.api_provider import APIProvider
from backend.services.agnes_client import chat_completion

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool definitions for the AI
# ---------------------------------------------------------------------------

TOOL_GENERATE_IMAGE = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generate an image based on a text description. Use when the user asks to create, draw, or generate an image.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed description of the image to generate",
                },
                "size": {
                    "type": "string",
                    "enum": ["1024x1024", "1792x1024", "1024x1792"],
                    "description": "Image dimensions",
                },
                "style": {
                    "type": "string",
                    "description": "Artistic style for the image (e.g., realistic, anime, oil painting)",
                },
            },
            "required": ["prompt"],
        },
    },
}

TOOL_GENERATE_VIDEO = {
    "type": "function",
    "function": {
        "name": "generate_video",
        "description": "Generate a video based on a text description. Use when the user asks to create, make, or generate a video.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed description of the video to generate",
                },
                "duration": {
                    "type": "integer",
                    "description": "Video duration in seconds",
                },
                "style": {
                    "type": "string",
                    "description": "Visual style for the video",
                },
            },
            "required": ["prompt"],
        },
    },
}

CHAT_TOOLS = [TOOL_GENERATE_IMAGE, TOOL_GENERATE_VIDEO]


# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------

def _sse_event(data: str | dict[str, Any], event: str | None = None) -> str:
    """Format a Server-Sent Event string."""
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    lines: list[str] = []
    if event:
        lines.append(f"event: {event}")
    for line in data.split("\n"):
        lines.append(f"data: {line}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main chat stream
# ---------------------------------------------------------------------------

async def chat_stream(
    messages: list[dict[str, Any]],
    model: str,
    provider_id: str,
    user_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream chat completions with SSE, including tool call detection.

    Emits SSE events:
      - delta: partial text chunks
      - tool_call: a tool was requested by the AI
      - done: stream finished
      - error: an error occurred
    """
    async with async_session_factory() as session:
        provider = await _resolve_provider(session, provider_id)
        if provider is None:
            yield _sse_event({"error": "No active provider found"}, event="error")
            return

        try:
            stream = await chat_completion(
                provider=provider,
                messages=messages,
                model=model,
                stream=True,
                tools=CHAT_TOOLS,
            )
        except Exception as exc:
            logger.exception("Failed to start chat stream")
            yield _sse_event({"error": str(exc)}, event="error")
            return

        # Accumulate across chunks for tool-call detection
        accumulated_content: str = ""
        accumulated_tool_calls: list[dict[str, Any]] = []

        try:
            async for chunk in stream:
                if not chunk.startswith("data: "):
                    continue

                payload_str = chunk[6:]
                if payload_str == "[DONE]":
                    break

                try:
                    payload = json.loads(payload_str)
                except json.JSONDecodeError:
                    continue

                choices = payload.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})

                # Text delta
                content = delta.get("content", "")
                if content:
                    accumulated_content += content
                    yield _sse_event({"content": content}, event="delta")

                # Tool calls delta
                tool_calls_delta = delta.get("tool_calls", [])
                for tc in tool_calls_delta:
                    idx = tc.get("index", 0)
                    # Ensure accumulator list is large enough
                    while len(accumulated_tool_calls) <= idx:
                        accumulated_tool_calls.append(
                            {"id": "", "function": {"name": "", "arguments": ""}}
                        )
                    if "id" in tc and tc["id"]:
                        accumulated_tool_calls[idx]["id"] = tc["id"]
                    if "function" in tc:
                        if "name" in tc["function"] and tc["function"]["name"]:
                            accumulated_tool_calls[idx]["function"]["name"] = tc["function"]["name"]
                        if "arguments" in tc["function"]:
                            accumulated_tool_calls[idx]["function"]["arguments"] += tc["function"]["arguments"]

            # Emit tool calls if any were detected
            if accumulated_tool_calls:
                for tc in accumulated_tool_calls:
                    yield _sse_event(
                        {
                            "id": tc.get("id", ""),
                            "name": tc.get("function", {}).get("name", ""),
                            "arguments": tc.get("function", {}).get("arguments", ""),
                        },
                        event="tool_call",
                    )

            yield _sse_event({"content": accumulated_content}, event="done")

        except Exception as exc:
            logger.exception("Error during chat stream")
            yield _sse_event({"error": str(exc)}, event="error")


async def _resolve_provider(
    session: AsyncSession,
    provider_id: str | None,
) -> APIProvider | None:
    """Resolve the provider to use for chat."""
    if provider_id:
        result = await session.execute(
            select(APIProvider).where(
                APIProvider.id == provider_id,
                APIProvider.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    # Fall back to default provider
    result = await session.execute(
        select(APIProvider).where(
            APIProvider.is_default == True,  # noqa: E712
            APIProvider.is_active == True,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()