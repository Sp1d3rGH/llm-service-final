"""
Экземпляр Celery для Bot Service.
Использует RabbitMQ как брокер и Redis как бэкенд результатов.
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

import app.tasks.llm_tasks

# Автоматически находит и регистрирует задачи из пакета app.tasks
celery_app.autodiscover_tasks(["app.tasks"], force=True)

print("Registered tasks:", list(celery_app.tasks.keys()))