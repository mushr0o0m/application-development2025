import json
import os
from datetime import datetime

import aio_pika
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./broker.db")
RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
REPORT_EXCHANGE = "report"
REPORT_QUEUE = "cmd_order"

broker = AioPikaBroker(
    RABBIT_URL,
    exchange_name=REPORT_EXCHANGE,
    queue_name=REPORT_QUEUE,
)

# scheduler with label-based schedule source
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

# Модифицируем задачу, добавив расписание с помощью параметра `schedule`.
# Задача будет выполняться каждую минуту.

async def _load_report_rows() -> list[dict[str, object]]:
    engine = create_async_engine(DATABASE_URL, echo=False)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT report_at, order_id, count_product
                    FROM report_orders
                    ORDER BY report_at DESC, order_id
                    """
                )
            )
            rows = []
            for row in result:
                rows.append(
                    {
                        "report_at": row.report_at.isoformat(),
                        "order_id": str(row.order_id),
                        "count_product": int(row.count_product or 0),
                    }
                )
            return rows
    finally:
        await engine.dispose()


async def _publish_report(payload: dict) -> None:
    body = json.dumps(payload, default=str).encode()
    connection = await aio_pika.connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            REPORT_EXCHANGE,
            aio_pika.ExchangeType.TOPIC,
            durable=False,
        )
        queue = await channel.declare_queue(
            REPORT_QUEUE,
            durable=False,
            arguments={
                # Match existing queue config created by Taskiq broker (DLX to "<queue>.dead_letter").
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": f"{REPORT_QUEUE}.dead_letter",
            },
        )
        await queue.bind(exchange, routing_key=REPORT_QUEUE)
        message = aio_pika.Message(
            body=body,
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=REPORT_QUEUE)


@broker.task(
    schedule=[
        {
            "cron": "*/1 * * * *",  # every minute
            "args": ["Cron User"],  # function args
            "schedule_id": "greet_every_minute",  # unique schedule id
        }
    ]
)
async def my_scheduled_task(name: str = "cron") -> str:
    rows = await _load_report_rows()
    payload = {
        "report_generated_at": datetime.utcnow().isoformat(),
        "requested_by": name,
        "items": rows,
    }
    await _publish_report(payload)
    return f"sent order report with {len(rows)} rows"