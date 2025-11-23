from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
  def __init__(self, db: Session):
    self.db = db

  async def get_by_id(self, user_id: UUID) -> Optional[User]:
    return self.db.get(User, user_id)

  async def get_by_filter(self, count: int, page: int, **kwargs) -> list[User]:
    stmt = select(User)

    for key, value in kwargs.items():
      if value is None:
        continue
      if hasattr(User, key):
        stmt = stmt.where(getattr(User, key) == value)

    if count and count > 0:
      offset = max(page - 1, 0) * count
      stmt = stmt.limit(count).offset(offset)

    result = self.db.execute(stmt)
    return list(result.scalars().all())

  async def count(self, **kwargs) -> int:
    stmt = select(func.count()).select_from(User)

    for key, value in kwargs.items():
      if value is None:
        continue
      if hasattr(User, key):
        stmt = stmt.where(getattr(User, key) == value)

    result = self.db.execute(stmt)
    return result.scalar() or 0

  async def create(self, user_data: dict[str, Any]) -> User:
    user = User(**user_data)
    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)
    return user

  async def update(self, user_id: UUID, user_data: dict[str, Any]) -> User:
    user = await self.get_by_id(user_id)
    if not user:
      raise ValueError("User not found")

    for key, value in user_data.items():
      if value is None:
        continue
      if hasattr(User, key):
        setattr(user, key, value)

    self.db.commit()
    self.db.refresh(user)
    return user

  async def delete(self, user_id: UUID) -> None:
    user = await self.get_by_id(user_id)
    if not user:
      return

    self.db.delete(user)
    self.db.commit()