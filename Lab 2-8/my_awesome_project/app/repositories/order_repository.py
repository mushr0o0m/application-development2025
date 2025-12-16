"""Repository helpers for orders."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order


class OrderRepository:
    """Async CRUD helper around :class:`app.models.order.Order`."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Return a single order with its items."""

        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.order_items))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(self, count: int = 50, page: int = 1) -> list[Order]:
        """Return a page of orders ordered by creation time desc."""

        stmt = select(Order).order_by(Order.created_at.desc())
        if count and count > 0:
            stmt = stmt.limit(count).offset(max(page - 1, 0) * count)
        stmt = stmt.options(selectinload(Order.order_items))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Return total number of orders."""

        stmt = select(func.count(Order.id)).select_from(Order)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def create(self, data: dict[str, Any]) -> Order:
        """Create a new order."""

        order = Order(**data)
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def update_status(self, order_id: UUID, status: str) -> Optional[Order]:
        """Update status for an order."""

        order = await self.get_by_id(order_id)
        if not order:
            return None
        order.status = status
        await self.db.flush()
        await self.db.refresh(order)
        return order
