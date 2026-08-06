"""API Provider model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class APIProvider(Base):
    """External AI API provider configuration."""

    __tablename__ = "api_providers"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    provider_type: Mapped[str] = mapped_column(
        String(64),
        default="agnes",
    )
    base_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    api_key_encrypted: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    poll_url: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )