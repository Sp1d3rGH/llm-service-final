"""
Фабрика приложения FastAPI и lifespan для Auth Service.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import BaseHTTPException
from app.db.base import Base
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Создаём таблицы при старте (если ещё не созданы)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()


def create_app() -> FastAPI:
    """Собирает и возвращает готовое приложение FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
    )

    # Подключаем единственный роутер
    app.include_router(api_router)

    # Обработчик кастомных HTTP-исключений
    @app.exception_handler(BaseHTTPException)
    async def custom_http_exception_handler(request: Request, exc: BaseHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Глобальный обработчик непредвиденных ошибок
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Системная ручка проверки здоровья
    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


# Экземпляр приложения для uvicorn
app = create_app()