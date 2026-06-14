"""
Базовый декларативный класс для всех ORM-моделей SQLAlchemy.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовая модель, от которой наследуются все сущности."""

    # Можно добавить общие колонки или методы при необходимости
    pass