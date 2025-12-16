"""Pydantic schemas for user-related payloads and responses.

Contains request/response models used by controllers and services.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base fields shared by create/update user schemas."""

    username: str = Field(...)
    email: str = Field(...)
    description: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user (inherits required fields)."""


class UserUpdate(BaseModel):
    """Schema for partial user updates (all fields optional)."""

    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserResponse(BaseModel):
    """Response model returned for single user objects."""

    id: UUID
    username: str
    email: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
    }


class UserListResponse(BaseModel):
    """Response model for paginated lists of users."""

    users: list[UserResponse]
    total: int
