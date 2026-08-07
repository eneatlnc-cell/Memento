"""Thin Agnes AI client — direct proxy to the OpenAI-compatible endpoints.

No database, no encryption, no provider records. The API key lives in the
environment and is read at request time.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any
from urllib.parse import urlparse

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Generous timeout — image/video generation can be slow.
TIMEOUT = httpx.Timeout(300.0, connect=15.0)


def _headers() -> dict[str, str]:
    if not settings.agnes_api_key:
        raise RuntimeError(
            "AGNES_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return {
        "Authorization": f"Bearer {settings.agnes_api_key}",
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    return f"{settings.agnes_api_base_url.rstrip('/')}{path}"


def _base_domain() -> str:
    """Strip the /v1 suffix to get the domain root (for /agnesapi endpoint)."""
    base = settings.agnes_api_base_url.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    return base


# ── Chat (streaming) ────────────────────────────────────────────────
async def chat_stream(
    messages: list[dict[str, Any]],
    model: str,
) -> AsyncGenerator[str, None]:
    """Stream OpenAI-style SSE chunks straight through."""
    payload = {"messages": messages, "model": model, "stream": True}
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        async with client.stream(
            "POST", _url("/chat/completions"), json=payload, headers=_headers()
        ) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_text():
                if chunk:
                    yield chunk


# ── Image generation (synchronous) ──────────────────────────────────
async def generate_image(
    prompt: str,
    model: str,
    size: str,
    image: str | None = None,
) -> dict[str, Any]:
    """Generate an image. Returns Agnes' raw JSON response.

    Per official docs: response_format and image must go inside extra_body,
    NOT at the top level (top-level response_format causes a 400 error).
    """
    extra_body: dict[str, Any] = {"response_format": "url"}
    if image:
        extra_body["image"] = [image]  # array of URLs per docs

    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "extra_body": extra_body,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            _url("/images/generations"), json=payload, headers=_headers()
        )
        resp.raise_for_status()
        return resp.json()


# ── Video generation (async task + polling) ─────────────────────────
async def submit_video(
    prompt: str,
    model: str,
    image: str | None = None,
    width: int = 1152,
    height: int = 768,
    num_frames: int = 121,
    frame_rate: int = 24,
) -> dict[str, Any]:
    """Submit a video task. Returns Agnes' raw JSON (contains video_id/task_id).

    Per official docs:
    - For text-to-video: pass model, prompt, width, height, num_frames, frame_rate.
    - For image-to-video: add top-level `image` (string URL), no `mode` needed.
    - `mode` is only for keyframes workflow (uses extra_body.image array).
    - num_frames must follow the 8n+1 rule and be <= 441.
    - Agnes normalizes width/height to nearest supported resolution tier.
    """
    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }
    if image:
        payload["image"] = image  # top-level string for image-to-video
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(_url("/videos"), json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def query_video(task_id: str) -> dict[str, Any]:
    """Query a video task's status. Returns Agnes' raw JSON.

    Uses the recommended endpoint: GET /agnesapi?video_id=<VIDEO_ID>
    (Legacy endpoint GET /v1/videos/<TASK_ID> also works but video_id is preferred.)
    """
    url = f"{_base_domain()}/agnesapi?video_id={task_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(url, headers=_headers())
        resp.raise_for_status()
        return resp.json()
