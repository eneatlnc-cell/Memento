"""Video generation routes — submit + poll, no auth, no DB.

The backend never stores task state; the browser polls GET /api/videos/{id}
which forwards each query straight to Agnes.
"""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import agnes

router = APIRouter(prefix="/api", tags=["Videos"])

# Duration (seconds) → num_frames at 24fps, following the 8n+1 rule.
# Per official docs: num_frames must be <= 441 and follow 8n+1.
_DURATION_FRAMES = {
    3: 81,    # 3s ≈ 81 frames / 24fps
    5: 121,   # 5s ≈ 121 frames / 24fps
    10: 241,  # 10s ≈ 241 frames / 24fps
    18: 441,  # 18s ≈ 441 frames / 24fps (max)
}
_FRAME_RATE = 24


class VideoRequest(BaseModel):
    prompt: str
    model: str = "agnes-video-v2.0"
    image: str | None = None  # optional image URL for image-to-video
    width: int = 1152
    height: int = 768
    duration: int = 5  # seconds; mapped to num_frames internally


@router.post("/videos")
async def submit_video(body: VideoRequest) -> Any:
    """Submit a video generation task. Returns Agnes' raw JSON (task id)."""
    num_frames = _DURATION_FRAMES.get(body.duration, 121)
    try:
        return await agnes.submit_video(
            prompt=body.prompt,
            model=body.model,
            image=body.image,
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
        raise HTTPException(
            status_code=502,
            detail=f"[ConnectError] Cannot reach Agnes API: {exc}",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail=f"[Timeout] Agnes API timed out: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"[{type(exc).__name__}] {exc}",
        ) from exc


@router.get("/videos/{task_id}")
async def video_status(task_id: str) -> Any:
    """Poll a video task's status. Returns Agnes' raw JSON."""
    try:
        return await agnes.query_video(task_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Agnes returned {exc.response.status_code}: {_detail(exc)}",
        ) from exc
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"[ConnectError] Cannot reach Agnes API: {exc}",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail=f"[Timeout] Agnes API timed out: {exc}",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"[{type(exc).__name__}] {exc}",
        ) from exc


def _detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return exc.response.text
    except Exception:  # noqa: BLE001
        return str(exc)
