"""Background video polling service."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import async_session_factory
from backend.models.api_provider import APIProvider
from backend.models.generation import Generation
from backend.services.agnes_client import query_video

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Active polling tasks
# ---------------------------------------------------------------------------

_active_tasks: dict[str, asyncio.Task[None]] = {}

POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 120  # 10 minutes at 5s intervals


async def start_polling(
    generation_id: str,
    video_id: str,
    provider_id: str,
) -> None:
    """Start a background polling task for a video generation."""
    if video_id in _active_tasks:
        logger.warning("Polling already active for video_id=%s", video_id)
        return

    task = asyncio.create_task(
        _poll_loop(generation_id, video_id, provider_id)
    )
    _active_tasks[video_id] = task
    task.add_done_callback(lambda t: _active_tasks.pop(video_id, None))
    logger.info("Started polling for generation_id=%s video_id=%s", generation_id, video_id)


def stop_polling(video_id: str) -> bool:
    """Cancel a polling task by video_id."""
    task = _active_tasks.pop(video_id, None)
    if task is not None:
        task.cancel()
        logger.info("Stopped polling for video_id=%s", video_id)
        return True
    return False


async def _poll_loop(
    generation_id: str,
    video_id: str,
    provider_id: str,
) -> None:
    """Internal polling loop that checks video status and updates the DB."""
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        try:
            await asyncio.sleep(POLL_INTERVAL_SECONDS)

            async with async_session_factory() as session:
                # Look up provider
                provider_result = await session.execute(
                    select(APIProvider).where(APIProvider.id == provider_id)
                )
                provider = provider_result.scalar_one_or_none()
                if provider is None:
                    logger.error("Provider not found for polling: %s", provider_id)
                    return

                # Query remote API
                result = await query_video(provider, video_id)
                status = result.get("status", "unknown")

                # Update generation record
                gen_result = await session.execute(
                    select(Generation).where(Generation.id == generation_id)
                )
                gen = gen_result.scalar_one_or_none()
                if gen is None:
                    logger.error("Generation not found for polling: %s", generation_id)
                    return

                if status == "completed":
                    gen.status = "completed"
                    gen.result_url = result.get("video_url") or result.get("url")
                    gen.thumbnail_url = result.get("thumbnail_url")
                    await session.commit()
                    logger.info("Video generation completed: %s", generation_id)
                    return

                elif status == "failed":
                    gen.status = "failed"
                    await session.commit()
                    logger.warning("Video generation failed: %s", generation_id)
                    return

                else:
                    gen.status = "processing"
                    await session.commit()
                    logger.debug(
                        "Poll attempt %d/%d for %s: status=%s",
                        attempt,
                        MAX_POLL_ATTEMPTS,
                        generation_id,
                        status,
                    )

        except asyncio.CancelledError:
            logger.info("Polling cancelled for video_id=%s", video_id)
            return
        except Exception:
            logger.exception("Polling error for generation_id=%s", generation_id)

    # Exhausted attempts
    logger.warning("Polling exhausted for generation_id=%s, marking as failed", generation_id)
    try:
        async with async_session_factory() as session:
            gen_result = await session.execute(
                select(Generation).where(Generation.id == generation_id)
            )
            gen = gen_result.scalar_one_or_none()
            if gen:
                gen.status = "failed"
                await session.commit()
    except Exception:
        logger.exception("Failed to update exhausted generation %s", generation_id)