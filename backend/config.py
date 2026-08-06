"""Minimal configuration — reads everything from environment / .env."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Agnes AI (OpenAI-compatible). Free official API.
    agnes_api_base_url: str = "https://apihub.agnes-ai.com/v1"
    agnes_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
