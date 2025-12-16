"""FastStream worker that listens to product and order queues."""

from __future__ import annotations

# Ensure project root is on sys.path so `from app...` imports work when
# running the script directly: `python scripts/check_rabbit.py`.
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import asyncio
import logging
import os

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderQueueMessage
from app.schemas.product import ProductQueueMessage
from app.services.order_service import OrderService
from app.services.product_service import ProductService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./broker.db")
RABBIT_URL = os.getenv(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

broker = RabbitBroker(RABBIT_URL)
app = FastStream(broker)


async def _get_order_service(session: AsyncSession) -> OrderService:
    product_repo = ProductRepository(session)
    order_repo = OrderRepository(session)
    order_item_repo = OrderItemRepository(session)
    return OrderService(product_repo, order_repo, order_item_repo)


@broker.subscriber("product")
async def subscribe_product(message: ProductQueueMessage) -> None:
    """Handle product creation and updates from the queue."""

    async with async_session_factory() as session:
        service = ProductService(ProductRepository(session))
        try:
            action = message.action.lower()
            if action == "create":
                payload = {
                    "name": message.name,
                    "description": message.description,
                    "price": message.price,
                    "stock_quantity": message.stock_quantity,
                }
                await service.create_product({k: v for k, v in payload.items() if v is not None})
            elif action == "update":
                if not message.id:
                    raise ValueError("Product id is required for update")
                payload = {
                    "name": message.name,
                    "description": message.description,
                    "price": message.price,
                    "stock_quantity": message.stock_quantity,
                }
                await service.update_product(message.id, {k: v for k, v in payload.items() if v is not None})
            elif action == "out_of_stock":
                if not message.id:
                    raise ValueError("Product id is required to mark out of stock")
                await service.mark_out_of_stock(message.id)
            else:
                logger.warning("Unknown product action: %s", message.action)
                return
            await session.commit()
            logger.info("Processed product message action=%s id=%s", action, message.id)
        except Exception:
            await session.rollback()
            logger.exception("Failed to process product message")
            raise


@broker.subscriber("order")
async def subscribe_order(message: OrderQueueMessage) -> None:
    """Handle order creation and status updates from the queue."""

    async with async_session_factory() as session:
        service = await _get_order_service(session)
        try:
            action = message.action.lower()
            if action == "create":
                if not message.user_id or not message.address_id:
                    raise ValueError("user_id and address_id are required to create order")
                items = [
                    {"product_id": item.product_id, "quantity": item.quantity}
                    for item in message.items or []
                ]
                await service.create_order(message.user_id, message.address_id, items)
            elif action == "update_status":
                if not message.order_id or not message.status:
                    raise ValueError("order_id and status are required to update status")
                await service.update_status(message.order_id, message.status)
            else:
                logger.warning("Unknown order action: %s", message.action)
                return
            await session.commit()
            logger.info("Processed order message action=%s", action)
        except Exception:
            await session.rollback()
            logger.exception("Failed to process order message")
            raise


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())