"""Зависимости для получения SQLAlchemy-сессии в FastAPI."""

from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from app.db.session import async_session_factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    # У каждого запроса своя async-сессия для изоляции.
    async with async_session_factory() as session:
        yield session
