"""Video generation routes."""

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
from app.schemas.generation import GenerationResponse, VideoGenerationRequest
from app.services.agnes_client import generate_video, query_video as query_video_remote
from app.services.video_poller import start_polling, stop_polling

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/videos", tags=["Videos"])


@router.post("", response_model=GenerationResponse, status_code=status.HTTP_201_CREATED)
async def create_video_generation(
    body: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Submit a video generation task."""
    # Resolve provider
    provider = await _resolve_provider(db, body.provider_id)
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active provider available",
        )

    # Create generation record
    generation = Generation(
        user_id=current_user.id,
        type="video",
        prompt=body.prompt,
        model=body.model,
        params={
            "height": body.height,
            "width": body.width,
            "num_frames": body.num_frames,
            "frame_rate": body.frame_rate,
            "mode": body.mode,
        },
        mode=body.mode,
        image_input=body.image_url,
        status="pending",
        credits_consumed=0,
    )
    db.add(generation)
    await db.flush()

    # Submit to Agnes API
    try:
        result = await generate_video(
            provider=provider,
            prompt=body.prompt,
            model=body.model,
            height=body.height,
            width=body.width,
            num_frames=body.num_frames,
            frame_rate=body.frame_rate,
            image_url=body.image_url,
            mode=body.mode,
        )
    except Exception as exc:
        logger.exception("Video submission failed for generation_id=%s", generation.id)
        generation.status = "failed"
        await db.flush()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Video generation failed: {exc}",
        )

    video_id = result.get("video_id") or result.get("id") or result.get("task_id")
    generation.task_id = video_id
    generation.status = "processing"

    await db.flush()
    await db.refresh(generation)

    # Start background polling
    if video_id:
        start_polling(
            generation_id=generation.id,
            video_id=video_id,
            provider_id=provider.id,
        )

    return GenerationResponse.model_validate(generation)


@router.get("/{task_id}", response_model=GenerationResponse)
async def get_video_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Query the status of a video generation task."""
    result = await db.execute(
        select(Generation).where(
            Generation.task_id == task_id,
            Generation.user_id == current_user.id,
        )
    )
    generation = result.scalar_one_or_none()
    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video generation task not found",
        )
    return GenerationResponse.model_validate(generation)


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_video_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a video generation task."""
    result = await db.execute(
        select(Generation).where(
            Generation.task_id == task_id,
            Generation.user_id == current_user.id,
            Generation.type == "video",
        )
    )
    generation = result.scalar_one_or_none()
    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video generation task not found",
        )

    # Stop any active polling
    stop_polling(task_id)

    await db.delete(generation)
    await db.flush()

    return {"message": "Video task deleted successfully"}


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