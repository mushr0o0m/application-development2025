from __future__ import annotations

import os
from typing import AsyncIterator

from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from litestar import Litestar
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Настройка базы данных
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname"
)

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def provide_db_session() -> AsyncIterator[AsyncSession]:
    """Провайдер сессии базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    """Провайдер репозитория пользователей"""
    return UserRepository(db_session)


async def provide_user_service(user_repository: UserRepository) -> UserService:
    """Провайдер сервиса пользователей"""
    return UserService(user_repository)


app = Litestar(
    route_handlers=[UserController],
    dependencies={
        "db_session": Provide(provide_db_session),
        "user_repository": Provide(provide_user_repository),
        "user_service": Provide(provide_user_service),
    },
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
