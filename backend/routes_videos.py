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


class VideoRequest(BaseModel):
    prompt: str
    model: str = "agnes-video-v2.0"
    image: str | None = None  # optional image URL for image-to-video
    num_frames: int = 121  # ~5 seconds at 24fps (must follow 8n+1 rule)
    frame_rate: int = 24


@router.post("/videos")
async def submit_video(body: VideoRequest) -> Any:
    """Submit a video generation task. Returns Agnes' raw JSON (task id)."""
    try:
        return await agnes.submit_video(
            prompt=body.prompt,
            model=body.model,
            image=body.image,
            num_frames=body.num_frames,
            frame_rate=body.frame_rate,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=_detail(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Video submission failed: {exc}") from exc


@router.get("/videos/{task_id}")
async def video_status(task_id: str) -> Any:
    """Poll a video task's status. Returns Agnes' raw JSON."""
    try:
        return await agnes.query_video(task_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=_detail(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Video query failed: {exc}") from exc


def _detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return exc.response.text
    except Exception:  # noqa: BLE001
        return str(exc)
