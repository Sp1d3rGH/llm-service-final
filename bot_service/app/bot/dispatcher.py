"""
Сборка бота и диспетчера aiogram, подключение обработчиков.
"""

from aiogram import Bot, Dispatcher

from app.core.config import settings

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def setup_handlers() -> None:
    """Подключает все роутеры с обработчиками."""
    from app.bot.handlers import router as main_router

    dp.include_router(main_router)


# Выполняем подключение при импорте (или можно вызывать явно при старте)
setup_handlers()