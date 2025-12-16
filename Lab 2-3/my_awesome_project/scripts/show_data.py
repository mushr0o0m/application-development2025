"""Show products, orders and order_items from the configured DB.

Usage:
    ./.venv/bin/python scripts/show_data.py

Reads `DATABASE_URL` env var (defaults to `sqlite+aiosqlite:///./broker.db`).
"""

from __future__ import annotations

import asyncio
import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Product, Order, OrderItem

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./broker.db")


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("\nProducts:")
        res = await session.execute(select(Product))
        products = res.scalars().all()
        for p in products:
            print(p.id, p.name, p.stock_quantity, float(p.price))

        print("\nOrders:")
        res = await session.execute(select(Order))
        orders = res.scalars().all()
        for o in orders:
            print(o.id, o.user_id, o.address_id, o.status, float(o.total_amount))

        print("\nOrder items:")
        res = await session.execute(select(OrderItem))
        items = res.scalars().all()
        for it in items:
            print(it.order_id, it.product_id, it.quantity, float(it.unit_price))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
