"""Базовый класс SQLAlchemy для всех ORM-моделей проекта."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...
