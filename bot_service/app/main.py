"""
FastAPI-приложение Bot Service.
Предоставляет health-check и, возможно, другие служебные ручки.
Сам бот и Celery worker запускаются отдельными процессами.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan без активных действий — ресурсы управляются отдельно."""
    yield


def create_app() -> FastAPI:
    """Собирает и возвращает приложение FastAPI."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok"}

    return app

app = create_app()
