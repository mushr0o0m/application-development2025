from __future__ import annotations

from typing import Any, Iterable
from types import SimpleNamespace


class OrderService:
    def __init__(
        self,
        product_repository,
        order_repository,
        order_item_repository,
    ):
        self.product_repository = product_repository
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository

    async def create_order(self, user_id, address_id, items: Iterable[dict[str, Any]]):
        """Создаёт заказ с позициями.

        items: iterable of {'product_id': UUID, 'quantity': int}

        Поведение:
        - проверяет доступный сток для каждого продукта
        - если недостаточно — выбрасывает ValueError
        - иначе уменьшает сток через product_repository и создаёт заказ + позиции
        - возвращает созданный заказ
        """
        total = 0
        # собираем продукты и проверяем сток
        products = []
        for it in items:
            product = await self.product_repository.get_by_id(it["product_id"])
            if product is None:
                raise ValueError(f"Product not found: {it['product_id']}")
            qty = int(it.get("quantity", 1))
            if getattr(product, "stock_quantity", 0) < qty:
                raise ValueError(f"Insufficient stock for product {product.id}")
            line_total = float(getattr(product, "price", 0)) * qty
            total += line_total
            products.append((product, qty))

        # создаём заказ
        order_data = {"user_id": user_id, "address_id": address_id, "total_amount": total}
        order = await self.order_repository.create(order_data)

        # уменьшаем сток и создаём позиции
        for product, qty in products:
            new_stock = int(product.stock_quantity) - qty
            product.stock_quantity = new_stock
            # ожидаем, что репозиторий предоставляет метод для сохранения/обновления продукта
            if hasattr(self.product_repository, "update"):
                await self.product_repository.update(product.id, {"stock_quantity": new_stock})
            elif hasattr(self.product_repository, "save"):
                await self.product_repository.save(product)
            else:
                # попытаемся вызвать generic метод set_stock если есть
                if hasattr(self.product_repository, "set_stock"):
                    await self.product_repository.set_stock(product.id, new_stock)

            oi_data = {
                "order_id": order.id,
                "product_id": product.id,
                "quantity": qty,
                "unit_price": product.price,
            }
            await self.order_item_repository.create(oi_data)

        return order
