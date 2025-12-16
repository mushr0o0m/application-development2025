from decimal import Decimal

import pytest
from app.models import Address, Order, OrderItem, Product, User
from app.services.order_service import OrderService
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_order_empty_items(db_session):
    # подготовка пользователя и адреса
    user = User(username="ec_user", email="ec@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(user_id=user.id, street="St", city="C", country="Cnt")
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    # создадим примитивные 'репозитории' использующие DBsession методы
    class PR:
        def __init__(self, session):
            self.session = session

        async def get_by_id(self, pid):
            return await self.session.get(Product, pid)

        async def update(self, pid, data):
            obj = await self.session.get(Product, pid)
            for k, v in data.items():
                setattr(obj, k, v)
            self.session.add(obj)
            await self.session.flush()

    class OR:
        def __init__(self, session):
            self.session = session

        async def create(self, data):
            o = Order(**data)
            self.session.add(o)
            await self.session.flush()
            return o

    class OIR:
        def __init__(self, session):
            self.session = session

        async def create(self, data):
            oi = OrderItem(**data)
            self.session.add(oi)
            await self.session.flush()
            return oi

    svc = OrderService(PR(db_session), OR(db_session), OIR(db_session))

    # пустой список товаров => создаст заказ с total 0 и без позиций
    order = await svc.create_order(user.id, address.id, [])
    assert order is not None
    await db_session.refresh(order)
    # нет позиций
    res = await db_session.execute(
        select(OrderItem).where(OrderItem.order_id == order.id)
    )
    items = res.scalars().all()
    assert items == []
    assert float(order.total_amount) == 0


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(db_session):
    # подготовка
    user = User(username="is_user", email="is@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(user_id=user.id, street="S", city="C", country="X")
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    p = Product(name="LowStock", price=Decimal("5.00"), stock_quantity=1)
    db_session.add(p)
    await db_session.commit()
    await db_session.refresh(p)

    class PR:
        def __init__(self, session):
            self.session = session

        async def get_by_id(self, pid):
            return await self.session.get(Product, pid)

        async def update(self, pid, data):
            obj = await self.session.get(Product, pid)
            for k, v in data.items():
                setattr(obj, k, v)
            self.session.add(obj)
            await self.session.flush()

    class OR:
        def __init__(self, session):
            self.session = session

        async def create(self, data):
            o = Order(**data)
            self.session.add(o)
            await self.session.flush()
            return o

    class OIR:
        def __init__(self, session):
            self.session = session

        async def create(self, data):
            oi = OrderItem(**data)
            self.session.add(oi)
            await self.session.flush()
            return oi

    svc = OrderService(PR(db_session), OR(db_session), OIR(db_session))

    # попытаемся заказать 2 штуки при наличии 1 => ожидаем ValueError
    with pytest.raises(ValueError):
        await svc.create_order(
            user.id, address.id, [{"product_id": p.id, "quantity": 2}]
        )


@pytest.mark.asyncio
async def test_create_order_product_not_found(db_session):
    user = User(username="nf_user", email="nf@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    address = Address(user_id=user.id, street="S", city="C", country="X")
    db_session.add(address)
    await db_session.commit()
    await db_session.refresh(address)

    class PR:
        async def get_by_id(self, pid):
            return None

    class OR:
        async def create(self, data):
            o = Order(**data)
            db_session.add(o)
            await db_session.flush()
            return o

    class OIR:
        async def create(self, data):
            oi = OrderItem(**data)
            db_session.add(oi)
            await db_session.flush()
            return oi

    svc = OrderService(PR(), OR(), OIR())

    with pytest.raises(ValueError):
        await svc.create_order(
            user.id,
            address.id,
            [{"product_id": "00000000-0000-0000-0000-000000000000", "quantity": 1}],
        )
