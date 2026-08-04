"""Generation-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ImageGenerationRequest(BaseModel):
    """Request body for image generation."""

    prompt: str = Field(..., min_length=1, max_length=4096)
    model: str = Field(default="agnes-image-v1")
    size: str = Field(default="1024x1024")
    ratio: str | None = Field(default=None)
    image_url: str | None = Field(default=None, max_length=2048)
    mode: str = Field(default="text2image")
    response_format: str = Field(default="url")
    provider_id: str | None = Field(default=None)


class VideoGenerationRequest(BaseModel):
    """Request body for video generation."""

    prompt: str = Field(..., min_length=1, max_length=4096)
    model: str = Field(default="agnes-video-v1")
    height: int = Field(default=720, ge=64, le=4096)
    width: int = Field(default=1280, ge=64, le=4096)
    num_frames: int = Field(default=120, ge=1, le=600)
    frame_rate: int = Field(default=24, ge=1, le=120)
    image_url: str | None = Field(default=None, max_length=2048)
    mode: str = Field(default="text2video")
    provider_id: str | None = Field(default=None)


class GenerationResponse(BaseModel):
    """Single generation record returned by the API."""

    id: str
    user_id: str
    type: str
    prompt: str
    model: str
    params: dict | None = None
    mode: str
    image_input: str | None = None
    result_url: str | None = None
    thumbnail_url: str | None = None
    status: str
    task_id: str | None = None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerationListResponse(BaseModel):
    """Paginated list of generation records."""

    items: list[GenerationResponse]
    total: int
    page: int
    page_size: int