"""Address model mapping for user addresses.

Many ORM model classes are simple data holders without public methods.
"""

# pylint: disable=too-few-public-methods

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Address(Base):
    """ORM model that stores postal addresses for users."""

    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    street: Mapped[str] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=True)
    zip_code: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["User"] = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(street={self.street!r}, city={self.city!r}, country={self.country!r})"
