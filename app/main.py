"""Точка входа приложения и общее подключение FastAPI."""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis

from app.api.v1.router import api_router
from app.core.config import settings
from app.core import redis_client
from app.exceptions.base import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.exceptions.handlers import (
    bad_request_handler,
    conflict_handler,
    not_found_handler,
    permission_denied_handler,
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
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(BadRequestError, bad_request_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.include_router(api_router)
