"""Create DB tables for the async SQLAlchemy engine used by the worker/producer.

Usage:
    ./.venv/bin/python scripts/create_tables.py

It reads `DATABASE_URL` from environment (defaults to `sqlite+aiosqlite:///./broker.db`).
"""

from __future__ import annotations

import asyncio
import os
import sys
import pathlib

# Ensure project root is on sys.path so `from app...` imports work when
# running the script directly: `python scripts/create_tables.py`.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy.ext.asyncio import create_async_engine

from app.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./broker.db")


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # run_sync executes the sync metadata.create_all on the sync engine
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Tables created or already exist in:", DATABASE_URL)


if __name__ == "__main__":
    asyncio.run(main())
