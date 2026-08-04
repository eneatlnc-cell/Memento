"""Application configuration using pydantic-settings."""

from __future__ import annotations

import secrets
from typing import ClassVar

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        description="Async SQLAlchemy database URL",
    )

    # JWT
    JWT_SECRET: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        description="Secret key for JWT signing",
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    JWT_EXPIRATION_HOURS: int = Field(
        default=168,
        description="JWT token expiration in hours (default 7 days)",
    )

    # Encryption
    ENCRYPTION_KEY: str = Field(
        default_factory=lambda: secrets.token_hex(32),
        description="Fernet encryption key for API key storage",
    )

    # Default admin
    DEFAULT_ADMIN_USERNAME: str = Field(
        default="admin",
        description="Default admin username",
    )
    DEFAULT_ADMIN_PASSWORD: str = Field(
        default="admin123",
        description="Default admin password (change on first login)",
    )
    DEFAULT_ADMIN_EMAIL: str = Field(
        default="admin@creative-ai.com",
        description="Default admin email",
    )

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str, info: ValidationInfo) -> str:
        """Validate JWT_SECRET is non-empty and at least 32 characters."""
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET must be non-empty and at least 32 characters long")
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate ENCRYPTION_KEY is non-empty."""
        if not v:
            raise ValueError("ENCRYPTION_KEY must be non-empty")
        return v


settings = Settings()