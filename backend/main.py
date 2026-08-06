"""Memento Lite — single-process FastAPI app.

Serves the API and the static single-page frontend from one process.
No database, no auth: just a thin proxy to Agnes AI's three modalities.
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import routes_chat, routes_images, routes_videos
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("memento")

app = FastAPI(
    title="Memento Lite",
    description="Minimal multimodal test console for Agnes AI (chat / image / video).",
    version="1.0.0",
)

# Permissive CORS — same-origin in production, handy for split dev otherwise.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (registered before the static mount so /api/* wins).
app.include_router(routes_chat.router)
app.include_router(routes_images.router)
app.include_router(routes_videos.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "agnes_base_url": settings.agnes_api_base_url,
        "agnes_key_configured": "yes" if settings.agnes_api_key else "no",
    }


# Static single-page frontend — mounted last so it acts as a catch-all.
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
    logger.info("Serving frontend from %s", _static_dir)
else:
    logger.warning("static/ directory not found — API-only mode")
