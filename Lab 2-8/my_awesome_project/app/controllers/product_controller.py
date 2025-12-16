"""HTTP controller for products."""

from __future__ import annotations

from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from app.schemas import ProductListResponse, ProductResponse
from app.services.product_service import ProductService


class ProductController(Controller):
    path = "/products"

    @get()
    async def list_products(
        self,
        product_service: ProductService,
        count: int = Parameter(default=50, ge=1),
        page: int = Parameter(default=1, ge=1),
    ) -> ProductListResponse:
        products = await product_service.list(count=count, page=page)
        total = await product_service.count()
        return ProductListResponse(
            products=[ProductResponse.model_validate(p) for p in products],
            total=total,
        )

    @get("/{product_id:uuid}")
    async def get_product(
        self,
        product_service: ProductService,
        product_id: UUID,
    ) -> ProductResponse:
        product = await product_service.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductResponse.model_validate(product)
