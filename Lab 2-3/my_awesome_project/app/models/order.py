"""Order and OrderItem ORM models."""

# Many ORM model classes are simple data holders without public methods.
# Disable pylint's "too-few-public-methods" for this module.
# pylint: disable=too-few-public-methods

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Order(Base):
    """Representation of a customer's order."""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    address_id: Mapped[UUID] = mapped_column(
        ForeignKey("addresses.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    # Используем строки для отложенной загрузки
    user: Mapped["User"] = relationship("User", back_populates="orders")
    address: Mapped["Address"] = relationship("Address")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
    )

    def __repr__(self):
        return f"Order(id={self.id!r}, status={self.status}, total={self.total_amount})"


class OrderItem(Base):
    """Single item (product + quantity) within an order."""

    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(
        default=1,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    # Используем строки для отложенной загрузки
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return (
            f"OrderItem(product_id={self.product_id}, "
            f"quantity={self.quantity}, price={self.unit_price})"
        )
