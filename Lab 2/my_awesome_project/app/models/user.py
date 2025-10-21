from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(onupdate=datetime.now)

    addresses: Mapped[list["Address"]] = relationship(
        "Address", 
        back_populates="user"
    )
    
    orders: Mapped[list["Order"]] = relationship(
        "Order", 
        back_populates="user"
    )

    def __repr__(self):
        return f"User(username={self.username!r}, email={self.email!r})"