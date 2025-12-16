"""Business logic for products."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.repositories.product_repository import ProductRepository
from app.cache import get_cached, set_cached, delete_cached
from app.schemas import ProductResponse


class ProductService:
    """High-level operations for products."""

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    async def get_by_id(self, product_id: UUID):
        cache_key = f"product:{product_id}"
        cached = await get_cached(cache_key)
        if cached is not None:
            return cached

        product = await self.product_repository.get_by_id(product_id)
        if product is None:
            return None

        try:
            payload = ProductResponse.model_validate(product).model_dump()
            await set_cached(cache_key, payload, ex=600)
        except Exception:
            pass
        return product

    async def list(self, count: int = 50, page: int = 1):
        products = await self.product_repository.list(count=count, page=page)
        # cache individual products for faster subsequent single-item lookup
        try:
            for p in products:
                try:
                    cache_key = f"product:{p.id}"
                    payload = ProductResponse.model_validate(p).model_dump()
                    await set_cached(cache_key, payload, ex=600)
                except Exception:
                    continue
        except Exception:
            pass
        return products

    async def count(self) -> int:
        return await self.product_repository.count()

    async def create_product(self, product_data: dict[str, Any]):
        return await self.product_repository.create(product_data)

    async def update_product(self, product_id: UUID, data: dict[str, Any]):
        product = await self.product_repository.update(product_id, data)
        # update cache entry for this product
        try:
            cache_key = f"product:{product_id}"
            payload = ProductResponse.model_validate(product).model_dump()
            await set_cached(cache_key, payload, ex=600)
        except Exception:
            pass
        return product

    async def mark_out_of_stock(self, product_id: UUID):
        return await self.product_repository.mark_out_of_stock(product_id)
