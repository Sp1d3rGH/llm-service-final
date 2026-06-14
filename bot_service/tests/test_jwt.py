"""
Модульные тесты проверки JWT для Bot Service.
"""

import pytest
from app.core.jwt import decode_and_validate, InvalidTokenException
from app.core.config import settings
from jose import jwt
from datetime import datetime, timedelta, timezone


def create_valid_token(sub="123", role="user", expires_delta=None):
    """Вспомогательная: создаёт токен с теми же секретом и алгоритмом, что и Auth Service."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=10)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class TestDecodeAndValidate:
    """Тесты функции decode_and_validate."""

    def test_valid_token(self):
        token = create_valid_token(sub="42", role="admin")
        payload = decode_and_validate(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_expired_token(self):
        token = create_valid_token(sub="1", expires_delta=timedelta(seconds=-1))
        with pytest.raises(InvalidTokenException):
            decode_and_validate(token)

    def test_garbage_token(self):
        with pytest.raises(InvalidTokenException):
            decode_and_validate("not.a.jwt")

    def test_wrong_signature(self):
        # Токен, подписанный другим ключом
        fake_payload = {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
        fake_token = jwt.encode(fake_payload, "wrong-secret", algorithm="HS256")
        with pytest.raises(InvalidTokenException):
            decode_and_validate(fake_token)