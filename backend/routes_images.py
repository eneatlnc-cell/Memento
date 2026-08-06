"""Image generation route — synchronous, no auth, no DB."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import agnes

router = APIRouter(prefix="/api", tags=["Images"])


class ImageRequest(BaseModel):
    prompt: str
    model: str = "agnes-image-2.0-flash"
    size: str = "1024x1024"
    image: str | None = None  # optional image URL for image-to-image


@router.post("/images")
async def create_image(body: ImageRequest) -> Any:
    """Generate an image. Returns Agnes' raw JSON (data[].url)."""
    try:
        return await agnes.generate_image(
            prompt=body.prompt,
            model=body.model,
            size=body.size,
            image=body.image,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=_detail(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Image generation failed: {exc}") from exc


def _detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return exc.response.text
    except Exception:  # noqa: BLE001
        return str(exc)
