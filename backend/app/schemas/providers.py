"""API Provider Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProviderCreate(BaseModel):
    """Request body for creating a new API provider."""

    name: str = Field(..., min_length=1, max_length=128)
    provider_type: str = Field(default="agnes", max_length=64)
    base_url: str = Field(..., max_length=512)
    api_key: str | None = Field(default=None, max_length=512)
    poll_url: str | None = Field(default=None, max_length=512)
    is_active: bool = True
    is_default: bool = False
    sort_order: int = 0


class ProviderUpdate(BaseModel):
    """Request body for updating an API provider."""

    name: str | None = Field(default=None, max_length=128)
    provider_type: str | None = Field(default=None, max_length=64)
    base_url: str | None = Field(default=None, max_length=512)
    api_key: str | None = Field(default=None, max_length=512)
    poll_url: str | None = Field(default=None, max_length=512)
    is_active: bool | None = None
    is_default: bool | None = None
    sort_order: int | None = None


class ProviderResponse(BaseModel):
    """Public provider info returned by the API (key masked)."""

    id: str
    name: str
    provider_type: str
    base_url: str
    api_key_masked: str | None = None
    poll_url: str | None = None
    is_active: bool
    is_default: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}