"""Repository helpers for order items."""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OrderItem


class OrderItemRepository:
    """Async helper to create order items."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict[str, Any]) -> OrderItem:
        """Create an order item and return it."""

        order_item = OrderItem(**data)
        self.db.add(order_item)
        await self.db.flush()
        await self.db.refresh(order_item)
        return order_item
