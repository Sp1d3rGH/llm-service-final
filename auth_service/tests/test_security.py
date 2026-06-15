from datetime import timedelta

import pytest

from app.core.security import (
    InvalidTokenException,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """
    Тесты на хеширование и проверку паролей.
    """
    def test_hash_returns_different_from_plain(self):
        plain = "securepassword123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert hashed.startswith("$2")

    def test_verify_correct_password(self):
        plain = "correct_password"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_verify_incorrect_password(self):
        plain = "real_password"
        hashed = hash_password(plain)
        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    """
    Тесты на создание и декодирование JWT.
    """
    def test_create_and_decode_token(self):
        data = {"sub": "123", "role": "user"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload

    def test_decode_expired_token(self):
        data = {"sub": "123", "role": "user"}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        with pytest.raises(InvalidTokenException):
            decode_token(expired_token)

    def test_decode_invalid_signature(self):
        token = "eyJhbGciOiJIUzI1NiJ9.invalidpayload.signature"
        with pytest.raises(InvalidTokenException):
            decode_token(token)
