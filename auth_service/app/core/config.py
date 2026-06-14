"""
Централизованная конфигурация Auth Service.
Все параметры читаются из переменных окружения и .env-файла.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, получаемые из переменных окружения."""

    # Общие
    APP_NAME: str = "auth-service"
    ENV: str = "local"

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # База данных
    SQLITE_PATH: str = "./auth.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",   # игнорируем лишние переменные в .env
    )


# Синглтон с настройками — импортируется во все остальные модули
settings = Settings()