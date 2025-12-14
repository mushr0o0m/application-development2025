"""Database session helpers.

This module exposes a synchronous SQLAlchemy engine and a
``SessionLocal`` factory used by the application and tests. It also exposes
helpers to create tables and a small generator-based ``get_db`` helper used
by dependency injection systems.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables defined on the models' metadata.

    Useful in local development and tests to ensure the database schema is
    present before running queries.
    """

    Base.metadata.create_all(bind=engine)


def get_db():
    """Yield a DB session and ensure it is closed after use.

    This is a small helper designed to be used as a dependency provider in
    frameworks that support generator-based dependencies.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "create_tables", "get_db", "DATABASE_URL"]
