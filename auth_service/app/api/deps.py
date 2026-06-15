from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from app.core.security import InvalidTokenException, decode_token
from app.db.models import User
from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase

security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию БД с автоматическим закрытием.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_users_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """
    Возвращает экземпляр UserRepository, связанный с текущей сессией.
    """
    return UserRepository(session)


async def get_auth_uc(repo: UserRepository = Depends(get_users_repo)) -> AuthUseCase:
    """
    Возвращает экземпляр AuthUseCase с внедрённым репозиторием.
    """
    return AuthUseCase(repo)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    repo: UserRepository = Depends(get_users_repo),
) -> User:
    """
    Извлекает токен через HTTPBearer, декодирует и возвращает пользователя.
    """
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except InvalidTokenException as exc:
        message = str(exc)
        if "expired" in message.lower():
            raise TokenExpiredError(detail=message) from exc
        raise InvalidTokenError(detail=message) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError(detail="Token missing 'sub' claim")

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise InvalidTokenError(detail="Invalid user id in token")

    user = await repo.get_by_id(user_id_int)
    if not user:
        raise UserNotFoundError()
    return user
