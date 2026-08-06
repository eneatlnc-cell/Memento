"""Authentication-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Request body for user registration."""

    username: str = Field(..., min_length=3, max_length=128)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str = Field(default="", max_length=128)


class UserLogin(BaseModel):
    """Request body for user login."""

    username: str
    password: str


class UserResponse(BaseModel):
    """Public user profile returned by the API."""

    id: str
    username: str
    email: str
    nickname: str
    avatar_url: str | None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    must_change_password: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """Request body for password change."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)