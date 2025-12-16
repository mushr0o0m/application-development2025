"""Service layer for user-related operations.

This module provides a thin service façade on top of
:class:`app.repositories.user_repository.UserRepository` and exists to hold
business rules or transactional coordination in one place.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.models import User
from app.repositories.user_repository import UserRepository
from app.cache import get_cached, set_cached, delete_cached
from app.schemas import UserResponse


class UserService:
    """Facade over user repository exposing high-level user operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Return a user by id or ``None`` when not found."""
        cache_key = f"user:{user_id}"
        cached = await get_cached(cache_key)
        if cached is not None:
            return cached

        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            return None

        # serialise to dict via pydantic and store in cache for 1 hour
        try:
            payload = UserResponse.model_validate(user).model_dump()
            await set_cached(cache_key, payload, ex=3600)
        except Exception:
            # if serialisation fails, skip caching
            pass
        return user

    async def get_by_filter(self, count: int, page: int, **kwargs) -> list[User]:
        """Return paginated users matching provided filters."""

        return await self.user_repository.get_by_filter(
            count=count, page=page, **kwargs
        )

    async def count(self, **kwargs) -> int:
        """Return number of users matching provided filters."""

        return await self.user_repository.count(**kwargs)

    async def create(self, user_data: dict[str, Any]) -> User:
        """Create and return a new user from `user_data`."""
        user = await self.user_repository.create(user_data)
        # populate cache for the created user
        try:
            cache_key = f"user:{user.id}"
            payload = UserResponse.model_validate(user).model_dump()
            await set_cached(cache_key, payload, ex=3600)
        except Exception:
            pass
        return user

    async def update(self, user_id: UUID, user_data: dict[str, Any]) -> User:
        """Update an existing user and return the updated instance."""
        user = await self.user_repository.update(user_id, user_data)
        # invalidate cache for updated user
        try:
            cache_key = f"user:{user_id}"
            await delete_cached(cache_key)
        except Exception:
            pass
        return user

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by id."""
        await self.user_repository.delete(user_id)
        try:
            cache_key = f"user:{user_id}"
            await delete_cached(cache_key)
        except Exception:
            pass
