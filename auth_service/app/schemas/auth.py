"""
Pydantic-схемы для аутентификации: запросы и ответы.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Тело запроса на регистрацию."""

    email: EmailStr
    password: str = Field(...,
        min_length=8,
        max_length=16,
        description="Пароль пользователя, 8-16 символов",
    )


class TokenResponse(BaseModel):
    """Ответ, содержащий JWT-токен."""

    access_token: str
    token_type: str = "bearer"