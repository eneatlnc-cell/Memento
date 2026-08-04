"""FastAPI application entry point for Memento."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.routes import auth, chat, config, history, images, providers, videos


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: setup logging, initialise database."""
    setup_logging()
    await init_db()
    yield


app = FastAPI(
    title="Memento",
    description="AI-powered creative content generation platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)
app.include_router(images.router)
app.include_router(videos.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(providers.router)
app.include_router(config.router)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "Memento"}