"""Model describing application users.

Many ORM model classes are simple data holders without public methods.

Defines database mapped attributes for the ``users`` table and common
relationships to addresses and orders.
"""

# pylint: disable=too-few-public-methods

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    """ORM model for a user record."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user")

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self):
        """Return a compact user representation useful for debugging."""

        return f"User(username={self.username!r}, email={self.email!r})"
