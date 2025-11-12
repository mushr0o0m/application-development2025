from app.database.session import SessionLocal, engine
from app.models.base import Base
from app.models.user import User

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def create_sample_user():
    db = SessionLocal()
    try:
        user = User(email="test@example.com", name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.name} with ID: {user.id}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_user()
