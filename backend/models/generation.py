"""Generation / history model."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Generation(Base):
    """Image / video generation record."""

    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="image or video",
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    model: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    params: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="text2image",
        comment="text2image / image2image / text2video / image2video / keyframes",
    )
    image_input: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        default=None,
    )
    result_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        default=None,
    )
    thumbnail_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        default=None,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="pending",
        comment="pending / processing / completed / failed",
    )
    credits_consumed: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    task_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        default=None,
        index=True,
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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