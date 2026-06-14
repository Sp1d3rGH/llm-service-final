"""
Централизованная конфигурация Bot Service.
Все параметры читаются из переменных окружения и .env-файла.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие
    APP_NAME: str = "bot-service"
    ENV: str = "local"

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # JWT (только для проверки)
    JWT_SECRET: str
    JWT_ALG: str = "HS256"

    # Брокер и хранилище
    REDIS_URL: str
    RABBITMQ_URL: str

    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()