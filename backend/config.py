"""Minimal configuration — reads everything from environment / .env."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server only — Agnes API key & base URL are now per-request (from frontend headers)
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
