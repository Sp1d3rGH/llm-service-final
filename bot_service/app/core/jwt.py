from jose import JWTError, jwt

from app.core.config import settings


class InvalidTokenException(Exception):
    pass

def decode_and_validate(token: str) -> dict:
    """
    Проверяет подпись и срок действия JWT.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options={"require_exp": True},
        )
        return payload
    except JWTError as e:
        raise InvalidTokenException(str(e))
