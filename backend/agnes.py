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
    images: list[str] | None = None,
) -> dict[str, Any]:
    """Generate image. 0 images = t2i, 1 = i2i, 2+ = multi-image composition."""
    payload: dict[str, Any] = {
        "prompt": prompt,
        "model": model,
        "size": size,
        "ratio": ratio,
    }
    if images:
        payload["extra_body"] = {"image": images}
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
    keyframes: list[str] | None = None,
    width: int = 1152,
    height: int = 768,
    num_frames: int = 121,
    frame_rate: int = 24,
) -> dict[str, Any]:
    """Submit video task.

    - No image/keyframes: text-to-video
    - image (single): image-to-video (top-level ``image`` field)
    - keyframes (2+): keyframe animation (``extra_body.image`` + ``mode: keyframes``)
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
        payload["image"] = image
    if keyframes and len(keyframes) >= 2:
        payload["extra_body"] = {
            "image": keyframes,
            "mode": "keyframes",
        }
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


# ── Prompt enhancement (text model) ────────────────────────────────
_CONTEXT_MAP: dict[str, str] = {
    "image_t2i": (
        "Text-to-image generation.\n"
        "Structure: [Subject] + [Scene/Environment] + [Style] + [Lighting] "
        "+ [Composition] + [Quality]"
    ),
    "image_i2i": (
        "Image-to-image editing.\n"
        "Structure: [Change request] + [New style/scene] + [Elements to add "
        "or remove] + [Elements to preserve]"
    ),
    "image_multi": (
        "Multi-image composition.\n"
        "Structure: [Reference image roles] + [Target scene] + [Relationship "
        "between images] + [Style/Lighting/Composition]"
    ),
    "video_t2v": (
        "Text-to-video generation.\n"
        "Structure: [Subject] + [Action] + [Scene] + [Camera movement] + "
        "[Lighting] + [Style]"
    ),
    "video_i2v": (
        "Image-to-video generation.\n"
        "Describe what should move and which key subject elements should "
        "remain stable. Add [Camera movement] + [Style]."
    ),
    "video_keyframes": (
        "Keyframe animation.\n"
        "Describe the smooth transition relationship between keyframes. "
        "Add [Camera movement] + [Style]."
    ),
}


async def enhance_prompt(
    text: str,
    context: str,
    api_key: str,
) -> str:
    """Use agnes-2.0-flash to expand a short prompt into a precise English one."""
    structure = _CONTEXT_MAP.get(context, _CONTEXT_MAP["image_t2i"])
    system = (
        "You are a prompt engineer for AI image/video generation. "
        "Expand the user's short description into a precise English prompt.\n\n"
        f"Current scenario: {structure}\n\n"
        "Rules:\n"
        "1. Output plain English text only — no explanations, no quotes\n"
        "2. Follow the structure above strictly\n"
        "3. If the input is Chinese, translate to English\n"
        "4. Preserve the user's original intent — only expand and optimize\n"
        "5. Do not invent specific details the user didn't mention; "
        "use stylistic descriptions to fill gaps"
    )
    payload = {
        "model": "agnes-2.0-flash",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
        "max_tokens": 512,
        "temperature": 0.7,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
        resp = await client.post(
            _build_url("/chat/completions"),
            json=payload,
            headers=_build_headers(api_key),
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
