import httpx
import pytest
import respx

from app.core.config import settings
from app.services.openrouter_client import LLMClientException, get_llm_response


@pytest.mark.asyncio
async def test_get_llm_response_success():
    """
    Проверяет, что функция правильно отправляет запрос и извлекает ответ.
    """
    test_response_text = "Это ответ модели"
    mock_url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    with respx.mock:
        route = respx.post(mock_url).mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [
                        {"message": {"content": test_response_text}}
                    ]
                },
            )
        )

        result = await get_llm_response("Привет")
        assert result == test_response_text
        assert route.called
        request_payload = route.calls.last.request.content
        assert "Привет" in request_payload.decode()


@pytest.mark.asyncio
async def test_get_llm_response_http_error():
    """
    Проверяем, что ошибка сети вызывает LLMClientException.
    """
    mock_url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    with respx.mock:
        respx.post(mock_url).mock(
            return_value=httpx.Response(500, text="Internal Error"))

        with pytest.raises(LLMClientException):
            await get_llm_response("test")
