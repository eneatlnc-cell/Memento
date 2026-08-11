"""Image generation route — no auth, no DB."""
from __future__ import annotations

import base64
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel

from backend import agnes
from backend.creds import get_api_key

router = APIRouter(prefix="/api", tags=["Images"])


class ImageRequest(BaseModel):
    prompt: str
    model: str = "agnes-image-2.1-flash"
    size: str = "1K"
    ratio: str = "1:1"
    images: list[str] | None = None  # 0=t2i, 1=i2i, 2+=multi-image


class EnhanceRequest(BaseModel):
    text: str
    context: str  # image_t2i | image_i2i | image_multi | video_t2v | video_i2v | video_keyframes


@router.post("/images")
async def create_image(
    body: ImageRequest,
    api_key: str = Depends(get_api_key),
) -> Any:
    try:
        return await agnes.generate_image(
            prompt=body.prompt,
            model=body.model,
            size=body.size,
            api_key=api_key,
            ratio=body.ratio,
            images=body.images,
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


@router.post("/enhance")
async def enhance_prompt(
    body: EnhanceRequest,
    api_key: str = Depends(get_api_key),
) -> dict[str, str]:
    """Use agnes-2.0-flash to expand a short prompt into a precise English one."""
    try:
        result = await agnes.enhance_prompt(
            text=body.text,
            context=body.context,
            api_key=api_key,
        )
        return {"prompt": result}
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


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload an image, return Data URI base64. No file stored."""
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
