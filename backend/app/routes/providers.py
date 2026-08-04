"""API Provider management routes (admin)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import encrypt_api_key, mask_api_key
from app.models.api_provider import APIProvider
from app.models.user import User
from app.routes.auth import get_current_user
from app.schemas.providers import ProviderCreate, ProviderResponse, ProviderUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["Providers"])


def _require_admin(current_user: User) -> None:
    """Raise 403 if the current user is not an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


def _to_response(provider: APIProvider) -> ProviderResponse:
    """Convert a model to a response with masked API key."""
    data = ProviderResponse.model_validate(provider)
    if provider.api_key_encrypted:
        data.api_key_masked = mask_api_key(provider.api_key_encrypted[:20])
    return data


@router.get("", response_model=list[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all API providers."""
    _require_admin(current_user)
    result = await db.execute(
        select(APIProvider).order_by(APIProvider.sort_order)
    )
    providers = result.scalars().all()
    return [_to_response(p) for p in providers]


@router.post("", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    body: ProviderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Add a new API provider."""
    _require_admin(current_user)

    provider = APIProvider(
        name=body.name,
        provider_type=body.provider_type,
        base_url=body.base_url,
        api_key_encrypted=encrypt_api_key(body.api_key) if body.api_key else None,
        poll_url=body.poll_url,
        is_active=body.is_active,
        is_default=body.is_default,
        sort_order=body.sort_order,
    )
    db.add(provider)
    await db.flush()
    await db.refresh(provider)

    logger.info("Provider created: %s", provider.id)
    return _to_response(provider)


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    body: ProviderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update an existing API provider."""
    _require_admin(current_user)

    result = await db.execute(
        select(APIProvider).where(APIProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    update_data = body.model_dump(exclude_unset=True)

    if "api_key" in update_data and update_data["api_key"] is not None:
        update_data["api_key_encrypted"] = encrypt_api_key(update_data.pop("api_key"))
    elif "api_key" in update_data:
        update_data.pop("api_key")

    for key, value in update_data.items():
        setattr(provider, key, value)

    await db.flush()
    await db.refresh(provider)

    logger.info("Provider updated: %s", provider_id)
    return _to_response(provider)


@router.delete("/{provider_id}", status_code=status.HTTP_200_OK)
async def delete_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete an API provider."""
    _require_admin(current_user)

    result = await db.execute(
        select(APIProvider).where(APIProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    await db.delete(provider)
    await db.flush()

    logger.info("Provider deleted: %s", provider_id)
    return {"message": "Provider deleted successfully"}


@router.post("/{provider_id}/set-default", response_model=ProviderResponse)
async def set_default_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Set a provider as the default."""
    _require_admin(current_user)

    result = await db.execute(
        select(APIProvider).where(APIProvider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )

    # Unset existing defaults
    await db.execute(
        update(APIProvider).where(APIProvider.is_default == True).values(is_default=False)  # noqa: E712
    )

    provider.is_default = True
    await db.flush()
    await db.refresh(provider)

    logger.info("Default provider set to: %s", provider_id)
    return _to_response(provider)