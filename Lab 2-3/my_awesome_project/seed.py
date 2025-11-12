from datetime import datetime
from app.database.session import engine
from app.models.user import User
from app.models.address import Address
from sqlalchemy.orm import sessionmaker
from app.models import Base

def seed():
    Base.metadata.create_all(bind=engine)
    
    session_factory = sessionmaker(engine)
    
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
    
    with session_factory() as session:
        try:
            for user_data in users_data:
                current_time = datetime.utcnow()
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
                        **{k: v for k, v in address_data.items() if k not in ['created_at', 'updated_at']}
                    )
                    session.add(address)
            
            session.commit()
                
        except Exception as e:
            session.rollback()
            raise

if __name__ == "__main__":
    seed()