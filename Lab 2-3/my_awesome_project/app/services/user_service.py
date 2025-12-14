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


class UserService:
    """Facade over user repository exposing high-level user operations."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Return a user by id or ``None`` when not found."""

        return await self.user_repository.get_by_id(user_id)

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

        return await self.user_repository.create(user_data)

    async def update(self, user_id: UUID, user_data: dict[str, Any]) -> User:
        """Update an existing user and return the updated instance."""

        return await self.user_repository.update(user_id, user_data)

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by id."""

        await self.user_repository.delete(user_id)
