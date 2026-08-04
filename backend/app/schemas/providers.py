"""API Provider Pydantic schemas."""

from __future__ import annotations

import ipaddress
import urllib.parse
from datetime import datetime
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


_PRIVATE_RANGES_V4 = [
    ipaddress.IPv4Network("127.0.0.0/8"),
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("169.254.0.0/16"),
]

_PRIVATE_RANGES_V6 = [
    ipaddress.IPv6Network("::1"),
    ipaddress.IPv6Network("fc00::/7"),
]


def _validate_not_private_url(url: AnyHttpUrl | str) -> AnyHttpUrl | str:
    """Validate that a URL does not point to a private/internal IP address."""
    url_str = str(url)
    parsed = urllib.parse.urlparse(url_str)
    host = parsed.hostname
    if not host:
        return url
    if host.lower() == "localhost":
        raise ValueError(f"URL resolves to localhost: {url_str!r}")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return url
    if isinstance(addr, ipaddress.IPv4Address):
        for net in _PRIVATE_RANGES_V4:
            if addr in net:
                raise ValueError(f"URL resolves to private IP: {url_str!r}")
    elif isinstance(addr, ipaddress.IPv6Address):
        for net in _PRIVATE_RANGES_V6:
            if addr in net:
                raise ValueError(f"URL resolves to private IP: {url_str!r}")
    return url


class ProviderCreate(BaseModel):
    """Request body for creating a new API provider."""

    name: str = Field(..., min_length=1, max_length=128)
    provider_type: str = Field(default="agnes", max_length=64)
    base_url: AnyHttpUrl
    api_key: str | None = Field(default=None, max_length=512)
    poll_url: str | None = Field(default=None, max_length=512)
    is_active: bool = True
    is_default: bool = False
    sort_order: int = 0

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: AnyHttpUrl) -> AnyHttpUrl:
        """Ensure base_url does not point to a private IP."""
        _validate_not_private_url(v)
        return v


class ProviderUpdate(BaseModel):
    """Request body for updating an API provider."""

    name: str | None = Field(default=None, max_length=128)
    provider_type: str | None = Field(default=None, max_length=64)
    base_url: AnyHttpUrl | None = None
    api_key: str | None = Field(default=None, max_length=512)
    poll_url: str | None = Field(default=None, max_length=512)
    is_active: bool | None = None
    is_default: bool | None = None
    sort_order: int | None = None

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: AnyHttpUrl | None) -> AnyHttpUrl | None:
        """Ensure base_url does not point to a private IP."""
        if v is not None:
            _validate_not_private_url(v)
        return v


class ProviderResponse(BaseModel):
    """Public provider info returned by the API (key masked)."""

    id: str
    name: str
    provider_type: str
    base_url: str
    api_key_masked: str | None = None
    poll_url: str | None = None
    is_active: bool
    is_default: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}