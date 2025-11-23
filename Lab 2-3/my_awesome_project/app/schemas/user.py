from __future__ import annotations

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(...)
    email: str = Field(...)
    description: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class UserResponse(BaseModel):
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
    users: list[UserResponse]
    total: int
