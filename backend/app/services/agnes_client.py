"""Agnes AI API client using httpx."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.core.security import decrypt_api_key
from app.models.api_provider import APIProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOMESTIC_BASE = "https://api.agnes-ai.com/v1"
INTERNATIONAL_BASE = "https://apihub.agnes-ai.com/v1"

DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _build_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _get_api_key(provider: APIProvider) -> str:
    """Decrypt and return the provider's API key, or raise an error."""
    if not provider.api_key_encrypted:
        raise ValueError(f"Provider '{provider.name}' has no API key configured")
    return decrypt_api_key(provider.api_key_encrypted)


# ---------------------------------------------------------------------------
# Image generation
# ---------------------------------------------------------------------------

async def generate_image(
    provider: APIProvider,
    prompt: str,
    model: str,
    size: str,
    ratio: str | None = None,
    image_url: str | None = None,
    response_format: str = "url",
) -> dict[str, Any]:
    """Generate an image via the Agnes AI API.

    Returns the parsed JSON response dict.
    """
    api_key = _get_api_key(provider)
    base = provider.base_url or DOMESTIC_BASE
    url = f"{base.rstrip('/')}/images/generations"

    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "response_format": response_format,
    }
    if ratio:
        payload["ratio"] = ratio
    if image_url:
        payload["image"] = image_url

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=_build_headers(api_key))
        resp.raise_for_status()
        data = resp.json()

    logger.info("Image generation succeeded, model=%s", model)
    return data


# ---------------------------------------------------------------------------
# Video generation (returns task_id / video_id)
# ---------------------------------------------------------------------------

async def generate_video(
    provider: APIProvider,
    prompt: str,
    model: str,
    height: int,
    width: int,
    num_frames: int,
    frame_rate: int,
    image_url: str | None = None,
    mode: str = "text2video",
) -> dict[str, Any]:
    """Submit a video generation task. Returns a dict with task_id/video_id."""
    api_key = _get_api_key(provider)
    base = provider.base_url or DOMESTIC_BASE
    url = f"{base.rstrip('/')}/videos"

    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "height": height,
        "width": width,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
        "mode": mode,
    }
    if image_url:
        payload["image"] = image_url

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.post(url, json=payload, headers=_build_headers(api_key))
        resp.raise_for_status()
        data = resp.json()

    logger.info("Video generation submitted, model=%s", model)
    return data


# ---------------------------------------------------------------------------
# Query video status
# ---------------------------------------------------------------------------

async def query_video(
    provider: APIProvider,
    video_id: str,
) -> dict[str, Any]:
    """Query the status of a video generation task."""
    api_key = _get_api_key(provider)
    base = provider.poll_url or provider.base_url or DOMESTIC_BASE
    url = f"{base.rstrip('/')}/videos/{video_id}"

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        resp = await client.get(url, headers=_build_headers(api_key))
        resp.raise_for_status()
        data = resp.json()

    return data


# ---------------------------------------------------------------------------
# Chat completion (streaming & non-streaming)
# ---------------------------------------------------------------------------

async def chat_completion(
    provider: APIProvider,
    messages: list[dict[str, Any]],
    model: str,
    stream: bool = False,
    tools: list[dict[str, Any]] | None = None,
) -> AsyncGenerator[str, None] | dict[str, Any]:
    """Send a chat completion request.

    When stream=True, returns an async generator yielding SSE chunks.
    When stream=False, returns the full parsed JSON response dict.
    """
    api_key = _get_api_key(provider)
    base = provider.base_url or DOMESTIC_BASE
    url = f"{base.rstrip('/')}/chat/completions"

    payload: dict[str, Any] = {
        "messages": messages,
        "model": model,
        "stream": stream,
    }
    if tools:
        payload["tools"] = tools

    if not stream:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=_build_headers(api_key))
            resp.raise_for_status()
            return resp.json()

    # Streaming response
    async def _stream() -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            async with client.stream("POST", url, json=payload, headers=_build_headers(api_key)) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        yield line

    return _stream()