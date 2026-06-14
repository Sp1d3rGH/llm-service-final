"""
Кастомные HTTP-исключения для Auth Service.
Все наследуются от BaseHTTPException, который, в свою очередь, от fastapi.HTTPException.
Используются в usecase и dependencies вместо прямого вызова HTTPException.
"""

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение с возможностью передачи деталей."""

    def __init__(self, detail: str = "", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь с таким email/username уже существует."""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class InvalidCredentialsError(BaseHTTPException):
    """Неверные учётные данные (логин/пароль)."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class InvalidTokenError(BaseHTTPException):
    """Токен недействителен (подпись, формат)."""

    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class TokenExpiredError(BaseHTTPException):
    """Токен истёк."""

    def __init__(self, detail: str = "Token expired"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден по указанному идентификатору."""

    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class PermissionDeniedError(BaseHTTPException):
    """Недостаточно прав для выполнения операции."""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)