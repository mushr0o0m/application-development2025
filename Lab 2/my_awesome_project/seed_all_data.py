from datetime import datetime
from decimal import Decimal
from app.database.session import engine
from app.models import Base
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.address import Address
from app.models.product import Product
from app.models.order import Order, OrderItem

def seed_all_data():
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(engine)
    
    with session_factory() as session:
        try:
            
            users_data = [
                {
                    "username": "alex_ivanov",
                    "email": "alex.ivanov@example.com",
                    "description": "Постоянный клиент с 2020 года",
                    "addresses": [
                        {
                            "street": "ул. Ленина, 25",
                            "city": "Москва",
                            "state": "Московская область",
                            "zip_code": "101000",
                            "country": "Россия",
                            "is_primary": True
                        }
                    ]
                },
                {
                    "username": "maria_petrova", 
                    "email": "maria.petrova@example.com",
                    "description": "Любитель художественной литературы",
                    "addresses": [
                        {
                            "street": "Невский пр., 100",
                            "city": "Санкт-Петербург",
                            "state": "Ленинградская область",
                            "zip_code": "190000",
                            "country": "Россия",
                            "is_primary": True
                        }
                    ]
                },
                {
                    "username": "sergey_sidorov",
                    "email": "sergey.sidorov@example.com", 
                    "description": "Спортсмен, активный покупатель",
                    "addresses": [
                        {
                            "street": "ул. Садовая, 45",
                            "city": "Екатеринбург",
                            "state": "Свердловская область", 
                            "zip_code": "620000",
                            "country": "Россия",
                            "is_primary": True
                        }
                    ]
                },
                {
                    "username": "olga_kuznetsova",
                    "email": "olga.kuznetsova@example.com",
                    "description": "Дизайнер и художник",
                    "addresses": [
                        {
                            "street": "ул. Советская, 10",
                            "city": "Новосибирск", 
                            "state": "Новосибирская область",
                            "zip_code": "630000",
                            "country": "Россия",
                            "is_primary": True
                        }
                    ]
                },
                {
                    "username": "dmitry_voronin",
                    "email": "dmitry.voronin@example.com",
                    "description": "IT-специалист, технологический энтузиаст",
                    "addresses": [
                        {
                            "street": "ул. Красноармейская, 75",
                            "city": "Казань",
                            "state": "Татарстан",
                            "zip_code": "420000", 
                            "country": "Россия",
                            "is_primary": True
                        }
                    ]
                }
            ]
            
            users = []
            for user_data in users_data:
                current_time = datetime.now()
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    description=user_data["description"],
                    created_at=current_time,
                    updated_at=current_time
                )
                session.add(user)
                session.flush()
                
                for address_data in user_data["addresses"]:
                    address = Address(
                        user_id=user.id,
                        created_at=current_time,
                        updated_at=current_time,
                        **address_data
                    )
                    session.add(address)
                
                users.append(user)

            products_data = [
                {
                    "name": "Ноутбук Dell XPS 13",
                    "description": "13-дюймовый ультрабук с процессором Intel Core i7",
                    "price": Decimal("125000.00"),
                    "stock_quantity": 10
                },
                {
                    "name": "Смартфон Samsung Galaxy S24",
                    "description": "Флагманский смартфон с камерой 200 МП",
                    "price": Decimal("89990.00"),
                    "stock_quantity": 25
                },
                {
                    "name": "Наушники Sony WH-1000XM5",
                    "description": "Беспроводные наушники с шумоподавлением",
                    "price": Decimal("29990.00"),
                    "stock_quantity": 30
                },
                {
                    "name": "Книга 'Чистый код' Роберт Мартин",
                    "description": "Руководство по написанию читаемого и поддерживаемого кода",
                    "price": Decimal("2500.00"),
                    "stock_quantity": 50
                },
                {
                    "name": "Игровая консоль PlayStation 5",
                    "description": "Новейшая игровая консоль от Sony",
                    "price": Decimal("64990.00"),
                    "stock_quantity": 15
                }
            ]
            
            products = []
            for product_data in products_data:
                current_time = datetime.now()
                product = Product(
                    **product_data,
                    created_at=current_time,
                    updated_at=current_time
                )
                session.add(product)
                products.append(product)
            
            session.flush()

            orders_data = [
                {
                    "user": users[0],
                    "address": users[0].addresses[0],
                    "status": "confirmed",
                    "items": [
                        {"product": products[0], "quantity": 1},
                        {"product": products[2], "quantity": 1}
                    ]
                },
                {
                    "user": users[1],
                    "address": users[1].addresses[0],
                    "status": "pending",
                    "items": [
                        {"product": products[3], "quantity": 2}
                    ]
                },
                {
                    "user": users[2],
                    "address": users[2].addresses[0],
                    "status": "shipped",
                    "items": [
                        {"product": products[1], "quantity": 1},
                        {"product": products[2], "quantity": 1}
                    ]
                },
                {
                    "user": users[3],
                    "address": users[3].addresses[0],
                    "status": "delivered",
                    "items": [
                        {"product": products[4], "quantity": 1}
                    ]
                },
                {
                    "user": users[4],
                    "address": users[4].addresses[0],
                    "status": "confirmed",
                    "items": [
                        {"product": products[0], "quantity": 1},
                        {"product": products[1], "quantity": 1},
                        {"product": products[2], "quantity": 1}
                    ]
                }
            ]
            
            for order_data in orders_data:
                current_time = datetime.now()
                order = Order(
                    user_id=order_data["user"].id,
                    address_id=order_data["address"].id,
                    status=order_data["status"],
                    created_at=current_time,
                    updated_at=current_time
                )
                session.add(order)
                session.flush()
                
                total_amount = Decimal("0")
                for item_data in order_data["items"]:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item_data["product"].id,
                        quantity=item_data["quantity"],
                        unit_price=item_data["product"].price
                    )
                    session.add(order_item)
                    total_amount += item_data["product"].price * item_data["quantity"]
                
                order.total_amount = total_amount
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            raise

if __name__ == "__main__":
    seed_all_data()