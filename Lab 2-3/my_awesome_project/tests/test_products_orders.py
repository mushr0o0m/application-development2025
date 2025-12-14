import pytest
from app.models import Address, Order, OrderItem, Product, User
from sqlalchemy import select


# Тест проверяет создание продукта и корректность полей (id, name)
@pytest.mark.asyncio
async def test_create_product(db_session):
    p = Product(name="Widget", description="A widget", price=9.99, stock_quantity=100)
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    assert p.id is not None
    assert p.name == "Widget"


# Тест проверяет обновление продукта (name и price)
@pytest.mark.asyncio
async def test_update_product(db_session):
    p = Product(name="Gadget", price=5.50)
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    p.name = "Gadget Pro"
    p.price = 6.50
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    assert p.name == "Gadget Pro"
    assert float(p.price) == 6.5


# Тест проверяет получение списка продуктов (минимум 2)
@pytest.mark.asyncio
async def test_list_products(db_session):
    # гарантирует, что есть несколько продуктов
    for i in range(2):
        db_session.add(Product(name=f"P{i}", price=1.0 + i))
    await db_session.commit()

    result = await db_session.execute(select(Product))
    products = result.scalars().all()
    assert len(products) >= 2


# Тест проверяет создание заказа с несколькими продуктами (несколько OrderItem), и корректность связей
@pytest.mark.asyncio
async def test_create_order_with_multiple_products(db_session):
    # создаём пользователя и адрес
    user = User(username="ord_user", email="ord_user@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(user_id=user.id, street="Main", city="Town", country="Country")
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    # создаём продукты
    p1 = Product(name="A", price=2.00)
    p2 = Product(name="B", price=3.00)
    db_session.add_all([p1, p2])
    await db_session.commit()
    await db_session.refresh(p1)
    await db_session.refresh(p2)

    # создаём заказ
    order = Order(user_id=user.id, address_id=address.id, total_amount=0)
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    # добавляем несколько позиций заказа
    oi1 = OrderItem(
        order_id=order.id, product_id=p1.id, quantity=2, unit_price=p1.price
    )
    oi2 = OrderItem(
        order_id=order.id, product_id=p2.id, quantity=1, unit_price=p2.price
    )
    db_session.add_all([oi1, oi2])
    # обновляем итоговую сумму заказа
    order.total_amount = (float(p1.price) * oi1.quantity) + (
        float(p2.price) * oi2.quantity
    )
    db_session.add(order)
    await db_session.commit()

    # проверяем наличие заказа и позиций
    result = await db_session.execute(select(Order).where(Order.id == order.id))
    found = result.scalars().first()
    assert found is not None

    result_items = await db_session.execute(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    items = result_items.scalars().all()
    assert len(items) == 2


# Тест проверяет получение конкретного заказа и удаление заказа вместе с ручным удалением его позиций
@pytest.mark.asyncio
async def test_get_and_delete_order(db_session):
    # создаём пользователя, адрес, продукт и заказ
    user = User(username="del_user", email="del_user@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(user_id=user.id, street="1st", city="City", country="Land")
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    p = Product(name="C", price=10)
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    order = Order(user_id=user.id, address_id=address.id, total_amount=10)
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)

    oi = OrderItem(order_id=order.id, product_id=p.id, quantity=1, unit_price=p.price)
    db_session.add(oi)
    await db_session.commit()

    # получаем заказ по id
    got = await db_session.get(Order, order.id)
    assert got is not None

    # удаляем заказ и его позиции
    # сначала удаляем позиции заказа, чтобы избежать ограничений целостности
    result_items = await db_session.execute(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    items = result_items.scalars().all()
    for it in items:
        await db_session.delete(it)
    await db_session.commit()

    await db_session.delete(got)
    await db_session.commit()

    should_be_none = await db_session.get(Order, order.id)
    assert should_be_none is None
