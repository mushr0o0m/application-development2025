import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models import Base
from app.repositories.user_repository import UserRepository
from litestar.testing import TestClient

@pytest.fixture(scope="session")
def engine(tmp_path_factory):
    """Create a temporary SQLite file for the test session to avoid collisions.

    Uses a fresh file under the pytest temp directory so running tests repeatedly
    won't conflict with leftover `test.db` files.
    """
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    return create_async_engine(db_url, echo=True)


@pytest.fixture
def async_session_maker(engine):
    """Session maker fixture expected by tests."""
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="session")
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(async_session_maker, tables) -> AsyncSession:
    # ensure the DB tables fixture runs before providing a session
    async with async_session_maker() as session:
        yield session

@pytest.fixture
def user_repository(db_session):
    return UserRepository(db_session)

@pytest.fixture
def client(async_session_maker, engine, tables):
    """Return a TestClient where the app's DB session factory is replaced
    with the test session maker so API tests use the temporary SQLite DB.
    """
    import main

    # Ensure test tables exist before creating client; patch app session factory and engine
    main.async_session_factory = async_session_maker
    main.engine = engine

    return TestClient(app=main.app)