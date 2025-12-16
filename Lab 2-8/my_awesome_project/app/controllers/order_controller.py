"""HTTP controller for orders."""

from __future__ import annotations

from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from app.schemas import OrderListResponse, OrderResponse
from app.services.order_service import OrderService


class OrderController(Controller):
    path = "/orders"

    @get()
    async def list_orders(
        self,
        order_service: OrderService,
        count: int = Parameter(default=50, ge=1),
        page: int = Parameter(default=1, ge=1),
    ) -> OrderListResponse:
        orders = await order_service.list(count=count, page=page)
        total = await order_service.count()
        return OrderListResponse(
            orders=[OrderResponse.model_validate(o) for o in orders],
            total=total,
        )

    @get("/{order_id:uuid}")
    async def get_order(
        self,
        order_service: OrderService,
        order_id: UUID,
    ) -> OrderResponse:
        order = await order_service.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return OrderResponse.model_validate(order)
