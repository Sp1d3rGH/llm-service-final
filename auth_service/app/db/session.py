from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

db_path = Path(settings.SQLITE_PATH).resolve()
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"


async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=(settings.ENV == "local"),
    connect_args={"check_same_thread": False},
    poolclass=None,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
