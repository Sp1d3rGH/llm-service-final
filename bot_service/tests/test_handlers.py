from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from jose import jwt

from app.bot.handlers import cmd_token, handle_message
from app.core.config import settings


def make_token(sub="123", expires_delta=None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=10)
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "role": "user", "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_mock_message(text: str, user_id: int = 12345, chat_id: int = 12345):
    """
    Создаёт мок-сообщение с минимальным набором атрибутов.
    """
    msg = MagicMock()
    msg.text = text
    msg.from_user.id = user_id
    msg.chat.id = chat_id
    msg.answer = AsyncMock()
    return msg


class TestTokenCommand:
    @pytest.mark.asyncio
    async def test_token_saved_in_redis(self, mock_get_redis):
        token = make_token(sub="42")
        msg = create_mock_message("/token " + token)
        command = MagicMock()
        command.args = token

        await cmd_token(message=msg, command=command)

        redis = mock_get_redis
        saved = await redis.get(f"jwt:{msg.from_user.id}")
        assert saved == token
        msg.answer.assert_called_once()
        assert "успешно" in msg.answer.call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_invalid_token_not_saved(self, mock_get_redis):
        msg = create_mock_message("/token garbage")
        command = MagicMock()
        command.args = "garbage"

        await cmd_token(message=msg, command=command)

        redis = mock_get_redis
        assert await redis.get(f"jwt:{msg.from_user.id}") is None
        msg.answer.assert_called_once()
        assert "недействителен" in msg.answer.call_args[0][0].lower()


class TestTextMessage:
    @pytest.mark.asyncio
    async def test_no_token_asks_auth(self, mock_get_redis, mocker):
        msg = create_mock_message("Как дела?")
        celery_mock = mocker.patch("app.tasks.llm_tasks.llm_request.delay")

        await handle_message(message=msg)

        celery_mock.assert_not_called()
        msg.answer.assert_called_once()
        called_text = msg.answer.call_args[0][0]
        assert "авторизация" in called_text.lower() or "/token" in called_text

    @pytest.mark.asyncio
    async def test_valid_token_calls_celery(self, mock_get_redis, mocker):
        token = make_token(sub="123")
        user_id = 999
        chat_id = 888

        redis = mock_get_redis
        await redis.setex(f"jwt:{user_id}", 3600, token)

        msg = create_mock_message("Привет, LLM!", user_id=user_id, chat_id=chat_id)
        celery_mock = mocker.patch("app.tasks.llm_tasks.llm_request.delay")

        await handle_message(message=msg)

        celery_mock.assert_called_once_with(tg_chat_id=chat_id, prompt="Привет, LLM!")
        msg.answer.assert_called_once()
        assert "принят" in msg.answer.call_args[0][0].lower()
