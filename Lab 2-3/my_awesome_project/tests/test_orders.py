import pytest
from decimal import Decimal
from datetime import datetime

from app.models import User, Address, Product, Order, OrderItem


@pytest.mark.asyncio
async def test_create_order_with_multiple_products(db_session):
    # Создаём тестового пользователя и адрес
    now = datetime.utcnow()
    user = User(username="test_user", email="test@example.com", created_at=now, updated_at=now)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(
        user_id=user.id,
        street="Test St",
        city="Test City",
        state="TS",
        zip_code="00000",
        country="Testland",
        is_primary=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    # Создаём два продукта с запасом
    p1 = Product(name="Prod A", description="A", price=Decimal("10.00"), stock_quantity=5)
    p2 = Product(name="Prod B", description="B", price=Decimal("20.00"), stock_quantity=3)
    db_session.add_all([p1, p2])
    await db_session.commit()
    await db_session.refresh(p1)
    await db_session.refresh(p2)

    # Создаём заказ
    order = Order(user_id=user.id, address_id=address.id, status="pending")
    db_session.add(order)
    await db_session.flush()

    # Добавляем две позиции заказа
    item1 = OrderItem(order_id=order.id, product_id=p1.id, quantity=2, unit_price=p1.price)
    item2 = OrderItem(order_id=order.id, product_id=p2.id, quantity=1, unit_price=p2.price)
    db_session.add_all([item1, item2])

    # Рассчитаем total_amount
    order.total_amount = item1.quantity * item1.unit_price + item2.quantity * item2.unit_price

    await db_session.commit()

    # Проверяем
    await db_session.refresh(order)
    assert len(order.order_items) == 2
    assert order.total_amount == Decimal("40.00")
