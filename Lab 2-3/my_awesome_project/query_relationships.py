from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker
from app.database.session import engine
from app.models.user import User
from app.models.address import Address

def query_relationships():
    
    session_factory = sessionmaker(engine)
    
    with session_factory() as session:
        print("ПОЛЬЗОВАТЕЛИ С АДРЕСАМИ:")
        print("=" * 60)
        
        stmt = select(User).options(selectinload(User.addresses))
        users = session.execute(stmt).scalars().all()
        
        for user in users:
            print(f"\nПользователь: {user.username}")
            print(f"Email: {user.email}")
            print(f"ID: {user.id}")
            print(f"Адреса ({len(user.addresses)}):")
            
            for address in user.addresses:
                primary_flag = "ОСНОВНОЙ" if address.is_primary else ""
                print(f"   Улица: {address.street}")
                print(f"   Город: {address.city}, {address.state}")
                print(f"   Индекс: {address.zip_code}, {address.country}")
                if primary_flag:
                    print(f"   {primary_flag}")
                print(f"   -------------------------")



if __name__ == "__main__":
    query_relationships()