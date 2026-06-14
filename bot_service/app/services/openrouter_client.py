"""
Клиент для взаимодействия с OpenRouter Chat Completions API.
"""

import httpx
from httpx import HTTPStatusError, RequestError

from app.core.config import settings


class LLMClientException(Exception):
    """Исключение при ошибке обращения к LLM."""
    pass


async def get_llm_response(user_message: str) -> str:
    """
    Отправляет сообщение пользователя в OpenRouter и возвращает ответ модели.

    :param user_message: текст сообщения пользователя.
    :return: ответ от LLM в виде строки.
    :raises LLMClientException: при сетевой ошибке или не-200 ответе.
    """
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": user_message}],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise LLMClientException(
                f"OpenRouter вернул статус {exc.response.status_code}: {exc.response.text}"
            )
        except RequestError as exc:
            raise LLMClientException(f"Ошибка сети при запросе к OpenRouter: {exc}")

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
        return content
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMClientException(f"Неожиданный формат ответа OpenRouter: {data}") from exc