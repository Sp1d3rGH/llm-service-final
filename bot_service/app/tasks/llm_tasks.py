"""
Celery-задача для обработки LLM-запроса и отправки ответа пользователю.
"""

import asyncio
import logging

import httpx

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import LLMClientException, get_llm_response

logger = logging.getLogger(__name__)


@celery_app.task(
    name="llm_request",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(LLMClientException, httpx.HTTPError),
)
def llm_request(self, tg_chat_id: int, prompt: str):
    """
    Отправляет prompt в OpenRouter, получает ответ и отправляет его в Telegram.
    При ошибках LLM автоматически делает повторные попытки.
    """
    # 1. Получить ответ LLM
    try:
        llm_answer = asyncio.run(get_llm_response(prompt))
    except (LLMClientException, httpx.HTTPError) as exc:
        logger.error(
            "LLM request failed (retry %d/%d): %s",
            self.request.retries,
            self.max_retries,
            exc,
        )
        raise self.retry(exc=exc)

    # 2. Отправить ответ пользователю в Telegram
    send_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": tg_chat_id,
        "text": llm_answer,
        "parse_mode": "HTML",
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(send_url, json=payload)
            resp.raise_for_status()
        logger.info("Sent LLM response to chat_id=%d", tg_chat_id)
    except Exception as exc:
        logger.error("Failed to send Telegram message: %s", exc)
        # Не ретраим всю задачу, так как ответ LLM уже получен