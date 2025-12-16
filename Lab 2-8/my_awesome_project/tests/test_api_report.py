import asyncio
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text

from app.models import Address, Order, OrderItem, Product, User


def test_report_endpoint_returns_rows(client, engine, async_session_maker):
    target_date = date.today()

    async def seed():
        async with engine.begin() as conn:
            await conn.execute(text("DROP VIEW IF EXISTS report_orders"))
            await conn.execute(
                text(
                    """
                    CREATE VIEW IF NOT EXISTS report_orders AS
                    SELECT
                        DATE(o.created_at) AS report_at,
                        o.id AS order_id,
                        COALESCE(SUM(oi.quantity), 0) AS count_product
                    FROM orders o
                    LEFT JOIN order_items oi ON oi.order_id = o.id
                    GROUP BY DATE(o.created_at), o.id
                    """
                )
            )

        async with async_session_maker() as session:
            user = User(username="report_user", email="report@example.com")
            session.add(user)
            await session.commit()
            await session.refresh(user)

            address = Address(
                user_id=user.id,
                street="R",
                city="C",
                country="X",
                created_at=datetime.combine(target_date, datetime.min.time()),
                updated_at=datetime.combine(target_date, datetime.min.time()),
            )
            session.add(address)
            await session.commit()
            await session.refresh(address)

            product = Product(name="ReportProd", price=Decimal("5.00"), stock_quantity=10)
            session.add(product)
            await session.commit()
            await session.refresh(product)

            order = Order(
                user_id=user.id,
                address_id=address.id,
                total_amount=Decimal("0.00"),
                created_at=datetime.combine(target_date, datetime.min.time()),
                updated_at=datetime.combine(target_date, datetime.min.time()),
            )
            session.add(order)
            await session.flush()

            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=2,
                unit_price=product.price,
            )
            session.add(item)
            order.total_amount = product.price * item.quantity
            await session.commit()

    asyncio.run(seed())

    resp = client.get(f"/report?report_date={target_date.isoformat()}")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["report_date"] == target_date.isoformat()
    assert payload["total"] == 1
    assert payload["items"][0]["count_product"] == 2
    assert payload["items"][0]["order_id"]

