"""
Обработчики сообщений Telegram-бота.
"""

import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.jwt import InvalidTokenException, decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

logger = logging.getLogger(__name__)

router = Router()


async def _is_authenticated(user_id: int) -> str | None:
    """
    Проверяет, есть ли у пользователя валидный JWT в Redis.
    Возвращает токен, если он валиден, иначе None.
    При ошибке проверки или истечении удаляет ключ из Redis.
    """
    redis = get_redis()
    token = await redis.get(f"jwt:{user_id}")
    if not token:
        return None

    try:
        decode_and_validate(token)
        return token
    except InvalidTokenException:
        # Токен не прошёл проверку (истёк или невалиден) — удаляем
        await redis.delete(f"jwt:{user_id}")
        return None


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message) -> None:
    """Приветственное сообщение."""
    await message.answer(
        "Привет! Я бот для консультаций с LLM.\n\n"
        "Чтобы начать, получи токен в Auth Service и отправь мне командой /token <твой JWT>.\n"
        "Затем просто пиши свой вопрос, и я передам его нейросети."
    )


@router.message(Command(commands=["token"]))
async def cmd_token(message: Message, command: CommandObject) -> None:
    """
    Принимает JWT-токен, проверяет его и сохраняет в Redis.
    Использование: /token <jwt>
    """
    if not command.args:
        await message.answer("Пожалуйста, укажи токен после команды: /token <jwt>")
        return

    token = command.args.strip()

    # 1. Проверяем токен
    try:
        payload = decode_and_validate(token)
    except InvalidTokenException as e:
        await message.answer(f"❌ Токен недействителен: {e}")
        return

    # 2. Вычисляем оставшееся время жизни токена
    exp = payload.get("exp")
    now = datetime.now(timezone.utc).timestamp()
    if not exp or exp <= now:
        await message.answer("❌ Токен уже истёк.")
        return

    ttl = int(exp - now)

    # 3. Сохраняем в Redis с TTL = оставшемуся сроку действия токена
    redis = get_redis()
    await redis.setex(f"jwt:{message.from_user.id}", ttl, token)

    await message.answer("✅ Токен успешно сохранён! Теперь ты можешь задавать вопросы.")


@router.message()
async def handle_message(message: Message) -> None:
    """
    Обрабатывает обычные текстовые сообщения.
    Проверяет наличие валидного токена и отправляет задачу в Celery.
    """
    user_id = message.from_user.id

    # Проверяем авторизацию
    token = await _is_authenticated(user_id)
    if not token:
        await message.answer(
            "⛔ Для доступа к LLM необходима авторизация.\n"
            "Получи токен в Auth Service и отправь мне командой /token <jwt>."
        )
        return

    # Отправляем задачу в Celery
    llm_request.delay(tg_chat_id=message.chat.id, prompt=message.text)
    await message.answer("⏳ Ваш запрос принят и обрабатывается. Ожидайте ответа...")