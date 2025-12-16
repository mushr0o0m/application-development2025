"""Business logic for products."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.repositories.product_repository import ProductRepository


class ProductService:
    """High-level operations for products."""

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def get_by_id(self, product_id: UUID):
        return await self.product_repository.get_by_id(product_id)

    async def list(self, count: int = 50, page: int = 1):
        return await self.product_repository.list(count=count, page=page)

    async def count(self) -> int:
        return await self.product_repository.count()

    async def create_product(self, product_data: dict[str, Any]):
        return await self.product_repository.create(product_data)

    async def update_product(self, product_id: UUID, data: dict[str, Any]):
        return await self.product_repository.update(product_id, data)

    async def mark_out_of_stock(self, product_id: UUID):
        return await self.product_repository.mark_out_of_stock(product_id)
