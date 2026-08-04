"""Async SQLAlchemy database engine, session, and initialisation."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Engine & Session
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """FastAPI dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables and seed default data (admin user, API provider)."""
    # Import all models so they are registered on Base.metadata
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created/verified")

    async with async_session_factory() as session:
        await _create_default_admin(session)
        await _create_default_provider(session)
        await session.commit()

    logger.info("Default data seeded")


async def _create_default_admin(session: AsyncSession) -> None:
    """Create default admin user if it does not exist."""
    from app.models.user import User
    from app.core.security import hash_password

    result = await session.execute(
        select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return

    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        email=settings.DEFAULT_ADMIN_EMAIL,
        nickname="Administrator",
        password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
        role="admin",
        must_change_password=True,
    )
    session.add(admin)
    logger.info(
        "Default admin user created (username=%s, password=***)",
        settings.DEFAULT_ADMIN_USERNAME,
    )


async def _create_default_provider(session: AsyncSession) -> None:
    """Create default API provider (Agnes AI) if it does not exist."""
    from app.models.api_provider import APIProvider

    result = await session.execute(
        select(APIProvider).where(APIProvider.name == "Agnes AI")
    )
    existing = result.scalar_one_or_none()
    if existing is not None:
        return

    provider = APIProvider(
        name="Agnes AI",
        provider_type="agnes",
        base_url="https://api.agnes-ai.com/v1",
        poll_url="https://api.agnes-ai.com/v1",
        is_active=True,
        is_default=True,
        sort_order=1,
    )
    session.add(provider)
    logger.info("Default API provider 'Agnes AI' created")