"""Image generation routes."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.api_provider import APIProvider
from app.models.generation import Generation
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.generation import GenerationResponse, ImageGenerationRequest
from app.services.agnes_client import generate_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["Images"])


@router.post("/generations", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_image_generation(
    body: ImageGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Generate an image (text-to-image or image-to-image)."""
    # Resolve provider
    provider = await _resolve_provider(db, body.provider_id)
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active provider available",
        )

    # Build the generation record
    generation = Generation(
        user_id=current_user.id,
        type="image",
        prompt=body.prompt,
        model=body.model,
        params={
            "size": body.size,
            "ratio": body.ratio,
            "mode": body.mode,
            "response_format": body.response_format,
        },
        mode=body.mode,
        image_input=body.image_url,
        status="pending",
        credits_consumed=0,
        task_id=None,
    )
    db.add(generation)
    await db.flush()

    # Call the Agnes API
    try:
        result = await generate_image(
            provider=provider,
            prompt=body.prompt,
            model=body.model,
            size=body.size,
            ratio=body.ratio,
            image_url=body.image_url,
            response_format=body.response_format,
        )
    except Exception as exc:
        logger.exception("Image generation failed for generation_id=%s", generation.id)
        generation.status = "failed"
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Image generation failed: {exc}",
        )

    # Update generation record with result
    generation.result_url = (
        result.get("data", [{}])[0].get("url")
        if isinstance(result.get("data"), list) and result["data"]
        else result.get("url")
    )
    generation.status = "completed"
    generation.task_id = result.get("id")

    await db.flush()
    await db.refresh(generation)

    return GenerationResponse.model_validate(generation)


async def _resolve_provider(
    db: AsyncSession,
    provider_id: str | None,
) -> APIProvider | None:
    """Resolve an active provider."""
    if provider_id:
        result = await db.execute(
            select(APIProvider).where(
                APIProvider.id == provider_id,
                APIProvider.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    result = await db.execute(
        select(APIProvider).where(
            APIProvider.is_default == True,  # noqa: E712
            APIProvider.is_active == True,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()