import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import create_app
from app.db.base import Base
from app.api.deps import get_db

# Создаём тестовый движок SQLite в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client():
    # Создаём таблицы перед каждым тестом
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Очищаем таблицы после теста (можно удалить все записи или не делать, т.к. in-memory)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
