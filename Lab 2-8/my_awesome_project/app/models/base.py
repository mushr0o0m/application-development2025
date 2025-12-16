"""Base ORM declarative class for the application's models.

Many ORM model classes are simple data holders without public methods.
"""

# pylint: disable=too-few-public-methods
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base used by all ORM models in the project."""
