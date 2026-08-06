"""Thin Agnes AI client — direct proxy to the OpenAI-compatible endpoints.

No database, no encryption, no provider records. The API key lives in the
environment and is read at request time.
"""
from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

# Generous timeout — image/video generation can be slow.
TIMEOUT = httpx.Timeout(180.0, connect=15.0)


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
            # Pass raw text chunks through unchanged so the browser's
            # EventSource-style parser sees the original `data: ...\n\n` framing.
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
    """Generate an image. Returns Agnes' raw JSON response."""
    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "response_format": "url",
    }
    if image:
        payload["image"] = image
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
    mode: str = "text2video",
) -> dict[str, Any]:
    """Submit a video task. Returns Agnes' raw JSON (contains a task id)."""
    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "mode": mode,
    }
    if image:
        payload["image"] = image
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(_url("/videos"), json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def query_video(task_id: str) -> dict[str, Any]:
    """Query a video task's status. Returns Agnes' raw JSON."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(
            _url(f"/videos/{task_id}"), headers=_headers()
        )
        resp.raise_for_status()
        return resp.json()
