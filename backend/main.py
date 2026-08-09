"""Memento Lite — single-process FastAPI app.

Serves the API and the static single-page frontend from one process.
No database, no auth: just a thin proxy to Agnes AI (image / video).
"""
from __future__ import annotations

import logging
from pathlib import Path

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend import routes_images, routes_videos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("memento")

app = FastAPI(
    title="Memento Lite",
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
app.include_router(routes_images.router)
app.include_router(routes_videos.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    # Stateless: API key lives in the frontend (localStorage) and is sent
    # per-request via X-Agnes-Key header. Base URL is hardcoded in agnes.py.
    return {"status": "ok"}


@app.get("/api/proxy")
async def proxy_media(url: str = Query(..., description="Media URL to proxy")):
    """Proxy media downloads to bypass CORS restrictions on mobile browsers.

    Agnes CDN URLs don't send CORS headers, so the browser blocks
    client-side fetch(). This endpoint fetches the URL server-side and
    streams the bytes back with permissive headers.
    """
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=15.0)) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "application/octet-stream")
        return StreamingResponse(
            iter([resp.content]),
            media_type=content_type,
            headers={"Content-Disposition": "attachment"},
        )


# Static single-page frontend — mounted last so it acts as a catch-all.
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")
    logger.info("Serving frontend from %s", _static_dir)
else:
    logger.warning("static/ directory not found — API-only mode")
