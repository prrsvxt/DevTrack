"""Точка входа приложения и общее подключение FastAPI."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.api.v1.router import api_router
from app.core.config import settings
from app.core import redis_client
from app.exceptions.handlers import (
    task_not_found_handler,
    task_permission_handler,
    invalid_pagination_handler,
)

from app.exceptions.task import (
    TaskNotFoundError,
    TaskPermissionError,
    InvalidPaginationError,
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Открывает Redis при старте и закрывает его при завершении."""
    redis_client_ = await redis_client.get_connection()
    app.state.redis = redis_client_
    print('redis connected')
    yield
    await app.state.redis.aclose()
    print('redis disconnected')

# Регистрируем обработчики доменных исключений один раз при запуске приложения.
app = FastAPI(title='DevTrack API', version='0.1.0', lifespan=lifespan)
app.add_exception_handler(TaskNotFoundError, task_not_found_handler)
app.add_exception_handler(TaskPermissionError, task_permission_handler)
app.add_exception_handler(InvalidPaginationError, invalid_pagination_handler)
app.include_router(api_router)
