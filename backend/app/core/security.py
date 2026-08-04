"""Security utilities for password hashing, JWT, and encryption."""

from __future__ import annotations

import base64
import binascii
import logging
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.fernet import Fernet

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Password hashing with bcrypt
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ---------------------------------------------------------------------------
# JWT token utilities
# ---------------------------------------------------------------------------

def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token. Returns the payload."""
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise ValueError("Invalid or expired token")


# ---------------------------------------------------------------------------
# Fernet encryption for API keys
# ---------------------------------------------------------------------------

def _get_fernet() -> Fernet:
    """Get a Fernet instance from the configured encryption key.

    Handles two key formats:
    - 44 chars: already a valid Fernet (url-safe base64-encoded) key
    - 64 hex chars: convert from hex to base64
    """
    key = settings.ENCRYPTION_KEY

    if len(key) == 44:
        # Already a valid Fernet key (32 bytes base64-url-encoded)
        return Fernet(key.encode("utf-8"))

    if len(key) == 64:
        # Hex-encoded: convert to raw bytes then base64-url-encode
        try:
            raw = binascii.unhexlify(key)  # 64 hex chars -> 32 bytes
            fernet_key = base64.urlsafe_b64encode(raw).decode("utf-8")
            return Fernet(fernet_key.encode("utf-8"))
        except (binascii.Error, ValueError):
            raise ValueError(
                "ENCRYPTION_KEY must be a 44-char Fernet key or 64-char hex string"
            )

    raise ValueError(
        "ENCRYPTION_KEY must be a 44-char Fernet key or 64-char hex string"
    )


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key using Fernet symmetric encryption."""
    f = _get_fernet()
    return f.encrypt(api_key.encode("utf-8")).decode("utf-8")


def decrypt_api_key(encrypted: str) -> str:
    """Decrypt a Fernet-encrypted API key."""
    f = _get_fernet()
    return f.decrypt(encrypted.encode("utf-8")).decode("utf-8")


# ---------------------------------------------------------------------------
# API key masking
# ---------------------------------------------------------------------------

def mask_api_key(key: str) -> str:
    """Return a masked version of an API key.

    Example: 'agn-abc123def4567890' -> 'agn****7890'
    """
    if len(key) <= 8:
        return "*" * len(key)
    prefix = key[:3]
    suffix = key[-4:]
    return f"{prefix}****{suffix}"