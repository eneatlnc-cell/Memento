"""Image generation route — synchronous, no auth, no DB."""
from __future__ import annotations

import base64
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from backend import agnes

router = APIRouter(prefix="/api", tags=["Images"])


class ImageRequest(BaseModel):
    prompt: str
    model: str = "agnes-image-2.0-flash"
    size: str = "1024x1024"
    image: str | None = None  # Data URI base64 or URL for image-to-image


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
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Agnes returned {exc.response.status_code}: {_detail(exc)}",
        ) from exc
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"[ConnectError] Cannot reach Agnes API: {exc}. Check DNS/firewall/network.",
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


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload an image file and return a Data URI base64 string.

    No file is stored — the base64 is passed directly to Agnes as image input.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")
    b64 = base64.b64encode(raw).decode()
    mime = file.content_type or "image/png"
    return {"data_uri": f"data:{mime};base64,{b64}"}


def _detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return exc.response.text
    except Exception:  # noqa: BLE001
        return str(exc)
