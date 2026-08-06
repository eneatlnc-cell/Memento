"""Platform configuration routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.get("")
async def get_platform_config() -> dict[str, Any]:
    """Return platform configuration including available models and options."""
    return {
        "models": {
            "image": [
                {"id": "agnes-image-v1", "name": "Agnes Image V1", "type": "image"},
                {"id": "agnes-image-v2", "name": "Agnes Image V2", "type": "image"},
            ],
            "video": [
                {"id": "agnes-video-v1", "name": "Agnes Video V1", "type": "video"},
            ],
            "chat": [
                {"id": "agnes-chat-v1", "name": "Agnes Chat V1", "type": "chat"},
            ],
        },
        "image_sizes": [
            {"value": "1024x1024", "label": "Square (1024x1024)"},
            {"value": "1792x1024", "label": "Wide (1792x1024)"},
            {"value": "1024x1792", "label": "Tall (1024x1792)"},
        ],
        "video_resolutions": [
            {"width": 1280, "height": 720, "label": "HD 720p"},
            {"width": 1920, "height": 1080, "label": "Full HD 1080p"},
        ],
        "modes": {
            "image": [
                {"value": "text2image", "label": "Text to Image"},
                {"value": "image2image", "label": "Image to Image"},
            ],
            "video": [
                {"value": "text2video", "label": "Text to Video"},
                {"value": "image2video", "label": "Image to Video"},
                {"value": "keyframes", "label": "Keyframes"},
            ],
        },
    }