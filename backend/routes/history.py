"""History routes for generation records."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.generation import Generation
from backend.models.user import User
from backend.routes.auth import get_current_user
from backend.schemas.generation import GenerationListResponse, GenerationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["History"])


class BatchDeleteRequest(BaseModel):
    """Request body for batch deletion of generation records."""

    ids: list[str] = Field(..., min_length=1, max_length=100)


@router.get("", response_model=GenerationListResponse)
async def get_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    type: str | None = Query(default=None, pattern="^(image|video)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get paginated generation history, optionally filtered by type."""
    # Build query
    query = select(Generation).where(Generation.user_id == current_user.id)
    count_query = select(func.count(Generation.id)).where(
        Generation.user_id == current_user.id
    )

    if type is not None:
        query = query.where(Generation.type == type)
        count_query = count_query.where(Generation.type == type)

    # Apply ordering and pagination
    query = query.order_by(Generation.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    # Execute
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(query)
    items = list(result.scalars().all())

    return GenerationListResponse(
        items=[GenerationResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{generation_id}", status_code=status.HTTP_200_OK)
async def delete_history_item(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a single generation record."""
    result = await db.execute(
        select(Generation).where(
            Generation.id == generation_id,
            Generation.user_id == current_user.id,
        )
    )
    generation = result.scalar_one_or_none()
    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation record not found",
        )

    await db.delete(generation)
    await db.flush()
    return {"message": "Record deleted successfully"}


@router.post("/batch-delete", status_code=status.HTTP_200_OK)
async def batch_delete_history(
    body: BatchDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Batch delete generation records."""
    result = await db.execute(
        select(Generation).where(
            Generation.id.in_(body.ids),
            Generation.user_id == current_user.id,
        )
    )
    generations = result.scalars().all()
    deleted_count = 0
    for gen in generations:
        await db.delete(gen)
        deleted_count += 1

    await db.flush()
    return {"message": f"Deleted {deleted_count} records", "deleted_count": deleted_count}