"""
Бизнес-логика аутентификации: регистрация, вход, получение профиля.
Использует UserRepository и функции безопасности.
"""

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import (
    InvalidTokenException,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.users import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserPublic


class AuthUseCase:
    """Содержит сценарии регистрации, входа и получения текущего пользователя."""

    def __init__(self, user_repo: UserRepository):
        self._repo = user_repo

    async def register(self, email: str, password: str) -> UserPublic:
        """
        Регистрирует нового пользователя.
        Если email уже занят — UserAlreadyExistsError.
        """
        existing = await self._repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()

        hashed = hash_password(password)
        try:
            user = await self._repo.create(email=email, password_hash=hashed)
        except IntegrityError:  # гонка данных, крайне редкий случай
            raise UserAlreadyExistsError()
        return UserPublic.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Аутентифицирует пользователя по email/паролю.
        При несовпадении — InvalidCredentialsError.
        Возвращает JWT-токен.
        """
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )
        return TokenResponse(access_token=access_token)

    async def me(self, token: str) -> UserPublic:
        """
        Возвращает профиль пользователя по JWT-токену.
        Если токен недействителен — InvalidTokenError.
        Если пользователь удалён или не найден — UserNotFoundError.
        """
        try:
            payload = decode_token(token)
        except InvalidTokenException as exc:
            raise InvalidTokenError(detail=str(exc))

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidTokenError(detail="Token missing 'sub' claim")

        try:
            user_id_int = int(user_id)
        except ValueError:
            raise InvalidTokenError(detail="Invalid user id in token")

        user = await self._repo.get_by_id(user_id_int)
        if not user:
            raise UserNotFoundError()
        return UserPublic.model_validate(user)