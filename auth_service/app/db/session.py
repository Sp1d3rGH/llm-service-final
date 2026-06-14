"""
Настройка асинхронного движка SQLAlchemy и фабрики сессий.
"""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Абсолютный путь к файлу SQLite из конфигурации
db_path = Path(settings.SQLITE_PATH).resolve()
# Строка подключения для aiosqlite
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# Асинхронный движок
async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=(settings.ENV == "local"),  # логи SQL только при локальной разработке
    connect_args={"check_same_thread": False},
    poolclass=None,  # для SQLite пул не используется (NullPool по умолчанию, но явно лучше)
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)