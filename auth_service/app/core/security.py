"""
Функции безопасности: хеширование паролей и работа с JWT.
Не содержат HTTP-зависимостей, только чистую логику.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Настройка CryptContext для bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidTokenException(Exception):
    """Поднимается, если токен невалиден или истёк."""
    pass


def hash_password(password: str) -> str:
    """Возвращает хеш пароля (bcrypt)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создаёт JWT-токен с полями sub, role, iat, exp.

    :param data: dict, содержащий минимум 'sub' и 'role'.
    :param expires_delta: опциональный срок жизни токена.
    :return: строка закодированного JWT.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"iat": now, "exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_token(token: str) -> dict:
    """
    Декодирует и проверяет JWT.

    :param token: строка токена.
    :return: расшифрованный payload.
    :raises InvalidTokenException: если токен недействителен (подпись, срок).
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
        return payload
    except JWTError as e:
        raise InvalidTokenException(str(e))