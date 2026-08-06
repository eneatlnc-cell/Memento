"""Application configuration using pydantic-settings."""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        description="Async SQLAlchemy database URL",
    )

    # JWT
    JWT_SECRET: str = Field(
        default="",
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
        default="",
        description="Fernet encryption key for API key storage",
    )

    # Default admin
    DEFAULT_ADMIN_USERNAME: str = Field(
        default="admin",
        description="Default admin username",
    )
    DEFAULT_ADMIN_PASSWORD: str = Field(
        default="",
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
        if not v:
            raise ValueError(
                "JWT_SECRET must be set. Generate: "
                "python -c 'import secrets; print(secrets.token_hex(32))'"
            )
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v

    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v: str, info: ValidationInfo) -> str:
        """Validate ENCRYPTION_KEY is non-empty and has valid length."""
        if not v:
            raise ValueError("ENCRYPTION_KEY must be non-empty")
        if len(v) not in (44, 64):
            raise ValueError(
                "ENCRYPTION_KEY must be a 44-char Fernet key or 64-char hex string"
            )
        return v

    @field_validator("DEFAULT_ADMIN_PASSWORD")
    @classmethod
    def validate_default_admin_password(cls, v: str, info: ValidationInfo) -> str:
        """Validate DEFAULT_ADMIN_PASSWORD is non-empty."""
        if not v:
            raise ValueError("DEFAULT_ADMIN_PASSWORD must be set")
        return v


settings = Settings()