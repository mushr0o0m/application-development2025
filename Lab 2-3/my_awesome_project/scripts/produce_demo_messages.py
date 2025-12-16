"""Produce sample product and order messages to RabbitMQ using pika.

The script sends 5 product creation messages and then 3 order creation
messages referencing those products. It also ensures there is at least one
user and address in the database so order creation succeeds on the
consumer side.
"""

from __future__ import annotations

# Ensure project root is on sys.path so `from app...` imports work when
# running the script directly: `python scripts/produce_demo_messages.py`.
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio
import json
import logging
import os
from typing import Iterable

import pika
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Address, Product, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./broker.db")
PRODUCT_QUEUE = "product"
ORDER_QUEUE = "order"


async def ensure_user_and_address(session: AsyncSession) -> tuple[User, Address]:
    """Ensure at least one user and address exist, creating them if necessary."""

    result = await session.execute(select(User).limit(1))
    user = result.scalars().first()
    if user is None:
        user = User(username="demo_user", email="demo@example.com")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info("Created demo user %s", user.id)

    result = await session.execute(
        select(Address).where(Address.user_id == user.id).limit(1)
    )
    address = result.scalars().first()
    if address is None:
        address = Address(user_id=user.id, street="Demo St", city="Demo City", country="Demo")
        session.add(address)
        await session.commit()
        await session.refresh(address)
        logger.info("Created demo address %s for user %s", address.id, user.id)

    return user, address


def publish_batch(routing_key: str, messages: Iterable[dict]) -> None:
    """Publish a batch of messages to the given routing key/queue."""

    params = pika.URLParameters(RABBIT_URL)
    with pika.BlockingConnection(params) as connection:
        channel = connection.channel()
        channel.queue_declare(queue=routing_key, durable=False)
        for msg in messages:
            body = json.dumps(msg, default=str)
            channel.basic_publish(
                exchange="",
                routing_key=routing_key,
                body=body.encode(),
                properties=pika.BasicProperties(content_type="application/json"),
            )
            logger.info("Published to %s: %s", routing_key, body)


async def wait_for_products(session: AsyncSession, names: list[str], timeout: float = 10.0) -> list[Product]:
    """Poll the DB until all products with the given names exist or timeout."""

    deadline = asyncio.get_event_loop().time() + timeout
    remaining = set(names)
    found: dict[str, Product] = {}

    while remaining and asyncio.get_event_loop().time() < deadline:
        result = await session.execute(select(Product).where(Product.name.in_(names)))
        products = result.scalars().all()
        for p in products:
            if p.name in remaining:
                found[p.name] = p
                remaining.discard(p.name)
        if remaining:
            await asyncio.sleep(0.5)

    return [found[n] for n in names if n in found]


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_factory() as session:
        user, address = await ensure_user_and_address(session)

    product_msgs = [
        {"action": "create", "name": "Product A", "description": "Demo A", "price": 10.0, "stock_quantity": 20},
        {"action": "create", "name": "Product B", "description": "Demo B", "price": 15.5, "stock_quantity": 15},
        {"action": "create", "name": "Product C", "description": "Demo C", "price": 7.25, "stock_quantity": 30},
        {"action": "create", "name": "Product D", "description": "Demo D", "price": 12.0, "stock_quantity": 8},
        {"action": "create", "name": "Product E", "description": "Demo E", "price": 20.0, "stock_quantity": 12},
    ]

    publish_batch(PRODUCT_QUEUE, product_msgs)

    # Wait for consumer to create products and fetch their ids
    async with async_session_factory() as session:
        products = await wait_for_products(session, [m["name"] for m in product_msgs])
        if len(products) < 3:
            raise RuntimeError("Not enough products created to build orders")

        orders = [
            {
                "action": "create",
                "user_id": str(user.id),
                "address_id": str(address.id),
                "items": [
                    {"product_id": str(products[0].id), "quantity": 2},
                    {"product_id": str(products[1].id), "quantity": 1},
                ],
            },
            {
                "action": "create",
                "user_id": str(user.id),
                "address_id": str(address.id),
                "items": [
                    {"product_id": str(products[2].id), "quantity": 3},
                    {"product_id": str(products[3].id), "quantity": 1},
                ],
            },
            {
                "action": "create",
                "user_id": str(user.id),
                "address_id": str(address.id),
                "items": [
                    {"product_id": str(products[4].id), "quantity": 1},
                ],
            },
        ]

    publish_batch(ORDER_QUEUE, orders)
    logger.info("Done. Published %d products and %d orders", len(product_msgs), len(orders))


if __name__ == "__main__":
    asyncio.run(main())
