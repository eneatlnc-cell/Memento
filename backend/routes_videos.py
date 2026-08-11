"""Video generation routes — submit + poll, no auth, no DB."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend import agnes
from backend.creds import get_api_key

router = APIRouter(prefix="/api", tags=["Videos"])

_DURATION_FRAMES = {3: 81, 5: 121, 10: 241, 18: 441}
_FRAME_RATE = 24


class VideoRequest(BaseModel):
    prompt: str
    model: str = "agnes-video-v2.0"
    image: str | None = None       # single image for image-to-video
    keyframes: list[str] | None = None  # 2+ images for keyframe animation
    width: int = 1152
    height: int = 768
    duration: int = 5


@router.post("/videos")
async def submit_video(
    body: VideoRequest,
    api_key: str = Depends(get_api_key),
) -> Any:
    num_frames = _DURATION_FRAMES.get(body.duration, 121)
    try:
        return await agnes.submit_video(
            prompt=body.prompt,
            model=body.model,
            api_key=api_key,
            image=body.image,
            keyframes=body.keyframes,
            width=body.width,
            height=body.height,
            num_frames=num_frames,
            frame_rate=_FRAME_RATE,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Agnes returned {exc.response.status_code}: {_detail(exc)}",
        ) from exc
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=502, detail=f"[ConnectError] {exc}") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail=f"[Timeout] {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"[{type(exc).__name__}] {exc}") from exc


@router.get("/videos/{task_id}")
async def video_status(
    task_id: str,
    api_key: str = Depends(get_api_key),
) -> Any:
    try:
        return await agnes.query_video(task_id, api_key)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Agnes returned {exc.response.status_code}: {_detail(exc)}",
        ) from exc
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=502, detail=f"[ConnectError] {exc}") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail=f"[Timeout] {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"[{type(exc).__name__}] {exc}") from exc


def _detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return exc.response.text
    except Exception:  # noqa: BLE001
        return str(exc)
