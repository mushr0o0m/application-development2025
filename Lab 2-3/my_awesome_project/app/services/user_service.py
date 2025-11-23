from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.models import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.user_repository.get_by_id(user_id)

    async def get_by_filter(self, count: int, page: int, **kwargs) -> list[User]:
        return await self.user_repository.get_by_filter(count=count, page=page, **kwargs)

    async def count(self, **kwargs) -> int:
        return await self.user_repository.count(**kwargs)

    async def create(self, user_data: dict[str, Any]) -> User:
        return await self.user_repository.create(user_data)

    async def update(self, user_id: UUID, user_data: dict[str, Any]) -> User:
        return await self.user_repository.update(user_id, user_data)

    async def delete(self, user_id: UUID) -> None:
        await self.user_repository.delete(user_id)
