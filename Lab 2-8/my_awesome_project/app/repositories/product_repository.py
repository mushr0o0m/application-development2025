"""Repository helpers for product entities."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product


class ProductRepository:
    """Async helper around :class:`app.models.product.Product`."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        """Return a single product by id."""

        return await self.db.get(Product, product_id)

    async def list(self, count: int = 50, page: int = 1) -> list[Product]:
        """Return a page of products ordered by name."""

        stmt = select(Product).order_by(Product.name)
        if count and count > 0:
            stmt = stmt.limit(count).offset(max(page - 1, 0) * count)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Return total number of products."""

        stmt = select(func.count(Product.id)).select_from(Product)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def create(self, data: dict[str, Any]) -> Product:
        """Create a product and return it."""

        product = Product(**data)
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def update(self, product_id: UUID, data: dict[str, Any]) -> Optional[Product]:
        """Update fields on a product and return it."""

        product = await self.get_by_id(product_id)
        if not product:
            return None

        for key, value in data.items():
            if value is None:
                continue
            if hasattr(product, key):
                setattr(product, key, value)

        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def mark_out_of_stock(self, product_id: UUID) -> Optional[Product]:
        """Mark a product as out of stock by setting quantity to zero."""

        return await self.update(product_id, {"stock_quantity": 0})
