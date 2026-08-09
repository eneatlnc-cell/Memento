"""Shared dependency — extract Agnes API key from request header.

The frontend sends X-Agnes-Key per request. Base URL is hardcoded in agnes.py.
This keeps the backend completely stateless (no .env, no config files).
"""
from __future__ import annotations

from fastapi import Header


def get_api_key(x_agnes_key: str = Header(default="", alias="X-Agnes-Key")) -> str:
    return x_agnes_key
