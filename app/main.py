"""Точка входа приложения и общее подключение FastAPI."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core import redis_client
from app.exceptions.base import BadRequestError, ConflictError, NotFoundError, PermissionDeniedError
from app.exceptions.handlers import (
    bad_request_handler,
    conflict_handler,
    invalid_credentials_handler,
    invalid_token_handler,
    not_found_handler,
    permission_denied_handler,
)
from app.exceptions.token import InvalidTokenError
from app.exceptions.user import InvalidCredentialsError


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Открывает Redis при старте и закрывает его при завершении."""
    redis_client_ = await redis_client.get_connection()
    app.state.redis = redis_client_
    logger.info('redis connected')
    yield
    await app.state.redis.aclose()
    logger.info('redis disconnected')


# Регистрируем обработчики доменных исключений один раз при запуске приложения.
app = FastAPI(title='DevTrack API', version='0.1.0', lifespan=lifespan)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(PermissionDeniedError, permission_denied_handler)
app.add_exception_handler(BadRequestError, bad_request_handler)
app.add_exception_handler(ConflictError, conflict_handler)
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
app.add_exception_handler(InvalidTokenError, invalid_token_handler)
app.include_router(api_router)
