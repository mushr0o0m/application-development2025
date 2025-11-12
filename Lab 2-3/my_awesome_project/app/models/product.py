from uuid import uuid4, UUID
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Product(Base):
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
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now)

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", 
        back_populates="product"
    )

    def __repr__(self):
        return f"Product(name={self.name!r}, price={self.price!r})"