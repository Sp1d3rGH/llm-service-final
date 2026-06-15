from aiogram import Bot, Dispatcher

from app.core.config import settings

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


def setup_handlers() -> None:
    """
    Подключает все роутеры с обработчиками.
    """
    from app.bot.handlers import router as main_router

    dp.include_router(main_router)

setup_handlers()
