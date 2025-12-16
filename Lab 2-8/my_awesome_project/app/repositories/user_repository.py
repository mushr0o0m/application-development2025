"""Repository for CRUD operations on :class:`app.models.user.User`.

Contains helper methods to query and modify users in the database.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    """Repository providing async CRUD helpers for users."""

    def __init__(self, db: AsyncSession):
        """Create a new repository with the given async DB session.

        Args:
            db: AsyncSession used to run queries and transactions.
        """
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Return a single user by its UUID or ``None`` if not found."""

        return await self.db.get(User, user_id)

    async def get_by_filter(self, count: int, page: int, **kwargs) -> list[User]:
        """Return a page of users filtered by provided keyword arguments.

        Args:
            count: number of items per page.
            page: 1-based page index.
            **kwargs: attributes to filter on (only attributes present on
                :class:`app.models.user.User` are applied).
        """

        stmt = select(User)

        for key, value in kwargs.items():
            if value is None:
                continue
            if hasattr(User, key):
                stmt = stmt.where(getattr(User, key) == value)

        if count and count > 0:
            offset = max(page - 1, 0) * count
            stmt = stmt.limit(count).offset(offset)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count(self, **kwargs) -> int:
        """Return number of users that match provided filters."""

        # Explicitly count a user column so pylint recognizes callable usage
        # pylint: disable=not-callable
        stmt = select(func.count(User.id)).select_from(User)

        for key, value in kwargs.items():
            if value is None:
                continue
            if hasattr(User, key):
                stmt = stmt.where(getattr(User, key) == value)

        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def create(self, user_data: dict[str, Any]) -> User:
        """Create a new user from the provided dict and return it."""

        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: dict[str, Any]) -> User:
        """Update an existing user with provided partial data."""

        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        for key, value in user_data.items():
            if value is None:
                continue
            if hasattr(User, key):
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by id if it exists."""

        user = await self.get_by_id(user_id)
        if not user:
            return

        await self.db.delete(user)
        await self.db.commit()
