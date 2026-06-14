"""
Репозиторий для работы с моделью User.
Содержит только операции чтения/записи в БД, без бизнес-логики и HTTP-исключений.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UserRepository:
    """Предоставляет методы доступа к таблице users."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Возвращает пользователя по id или None."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Возвращает пользователя по email или None."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        """
        Создаёт нового пользователя и сохраняет в БД.
        При нарушении уникальности email выбрасывается IntegrityError (из SQLAlchemy).
        """
        user = User(email=email, password_hash=password_hash, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user