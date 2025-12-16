"""Schemas for product payloads and queue messages."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Base fields shared by product create/update."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None


class ProductCreate(ProductBase):
    name: str = Field(...)
    price: Decimal = Field(...)


class ProductUpdate(ProductBase):
    """Partial update for product."""


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int


class ProductQueueMessage(BaseModel):
    """Queue payload for product changes."""

    action: str = Field(..., description="create|update|out_of_stock")
    id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
