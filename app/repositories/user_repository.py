"""Помощники доступа к данным для поиска пользователей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        # Используем индексированное поле для быстрого поиска по email.
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        # Username тоже уникален, поэтому запрос вернёт максимум одну запись.
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, email: str, username: str, hashed_password: str) -> User:
        # Сохранение в БД произойдёт позже, когда сервис сделает commit.
        user = User(email=email, username=username, hashed_password=hashed_password)
        self.session.add(user)
        return user

    async def get_by_id(self, id: int) -> User | None:
        # Ищем по первичному ключу для сценария с текущим пользователем.
        stmt = select(User).where(User.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
