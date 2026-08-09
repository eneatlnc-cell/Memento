"""Thin Agnes AI client — stateless proxy.

No database, no config files. The API key is passed in per
request from the frontend (via HTTP header); base URL is hardcoded here.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(300.0, connect=15.0)

BASE_URL = "https://api.agnes-ai.cn/v1"


def _build_headers(api_key: str) -> dict[str, str]:
    if not api_key:
        raise RuntimeError("未设置 API Key，请在页面顶部输入你的 API Key。")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _build_url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def _base_domain() -> str:
    """Strip the /v1 suffix for the /agnesapi polling endpoint."""
    base = BASE_URL.rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3]
    return base


# ── Image generation ────────────────────────────────────────────────
async def generate_image(
    prompt: str,
    model: str,
    size: str,
    api_key: str,
    ratio: str = "1:1",
    image: str | None = None,
) -> dict[str, Any]:
    extra_body: dict[str, Any] = {"response_format": "url"}
    if image:
        extra_body["image"] = [image]

    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "ratio": ratio,
        "extra_body": extra_body,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            _build_url("/images/generations"),
            json=payload,
            headers=_build_headers(api_key),
        )
        resp.raise_for_status()
        return resp.json()


# ── Video generation ────────────────────────────────────────────────
async def submit_video(
    prompt: str,
    model: str,
    api_key: str,
    image: str | None = None,
    width: int = 1152,
    height: int = 768,
    num_frames: int = 121,
    frame_rate: int = 24,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }
    if image:
        payload["image"] = image
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            _build_url("/videos"),
            json=payload,
            headers=_build_headers(api_key),
        )
        resp.raise_for_status()
        return resp.json()


async def query_video(
    task_id: str,
    api_key: str,
) -> dict[str, Any]:
    url = f"{_base_domain()}/agnesapi?video_id={task_id}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(url, headers=_build_headers(api_key))
        resp.raise_for_status()
        return resp.json()
