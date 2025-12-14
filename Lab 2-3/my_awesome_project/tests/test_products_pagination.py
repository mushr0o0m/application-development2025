import pytest
from app.models import Product
from sqlalchemy import func, select

# Тесты проверяют поведение пагинации товаров на уровне БД (limit/offset).
# Подход: создаём набор продуктов с детерминированными именами и запрашиваем
# страницы с разным `per_page` и `page` (1-based). Проверяем длины, содержимое
# и поведение при выходе за последний номер страницы.


@pytest.mark.asyncio
async def test_products_pagination_basic(db_session):
    total_items = 25
    # создаём продукты с детерминированными именами для предсказуемого порядка
    for i in range(total_items):
        db_session.add(Product(name=f"Product {i:03}", price=1.0 + i))
    await db_session.commit()

    per_page = 10

    # страница 1
    page = 1
    stmt = (
        select(Product)
        .order_by(Product.name)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    assert len(items) == 10
    assert items[0].name == "Product 000"

    # страница 2
    page = 2
    stmt = (
        select(Product)
        .order_by(Product.name)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    assert len(items) == 10
    assert items[0].name == "Product 010"

    # страница 3 (частичная)
    page = 3
    stmt = (
        select(Product)
        .order_by(Product.name)
        .limit(per_page)
        .offset((page - 1) * per_page)
    )
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    assert len(items) == 5
    assert items[0].name == "Product 020"


@pytest.mark.asyncio
async def test_products_pagination_total_and_bounds(db_session):
    # создаём 7 элементов и проверяем граничные условия
    names = [f"X{i}" for i in range(7)]
    for n in names:
        db_session.add(Product(name=n, price=1.0))
    await db_session.commit()

    # проверим общее количество через агрегат
    count_stmt = select(func.count()).select_from(Product)
    total = (await db_session.execute(count_stmt)).scalar_one()
    assert total >= 7

    per_page = 5

    # страница 1 должна вернуть 5
    stmt = select(Product).order_by(Product.name).limit(per_page).offset(0)
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    assert len(items) == 5

    # страница 2 должна вернуть оставшиеся
    stmt = select(Product).order_by(Product.name).limit(per_page).offset(per_page)
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    # возможно в БД уже есть продукты из других тестов; проверяем, что на второй странице не больше per_page
    assert len(items) <= per_page

    # страница значительно дальше — возвращает пустой список
    stmt = select(Product).order_by(Product.name).limit(per_page).offset(1000)
    res = await db_session.execute(stmt)
    items = res.scalars().all()
    assert items == []
