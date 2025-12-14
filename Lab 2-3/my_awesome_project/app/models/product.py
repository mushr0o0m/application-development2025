"""Product model and related mapping information.

Many ORM model classes are simple data holders without public methods.
"""

# pylint: disable=too-few-public-methods

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Product(Base):
    """ORM model that represents a sellable product."""

    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
        lazy="selectin",
    )

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price!r})"
