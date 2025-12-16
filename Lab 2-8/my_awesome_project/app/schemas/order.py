"""Schemas for orders and queue messages."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class OrderItemPayload(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class OrderQueueMessage(BaseModel):
    """Queue payload for creating or updating orders."""

    action: str = Field(..., description="create|update_status")
    order_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    address_id: Optional[UUID] = None
    items: Optional[list[OrderItemPayload]] = None
    status: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    address_id: UUID
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_items: list[OrderItemResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
