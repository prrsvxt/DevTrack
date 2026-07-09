"""Обработчики исключений FastAPI, возвращающие единый JSON-формат."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.base import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.exceptions.token import InvalidTokenError
from app.exceptions.user import InvalidCredentialsError


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc) or "Resource not found"},
    )


async def permission_denied_handler(
    request: Request, exc: PermissionDeniedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc) or "Permission denied"},
    )


async def bad_request_handler(request: Request, exc: BadRequestError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc) or "Bad request"},
    )


async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc) or "Conflict"},
    )


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc) or "Invalid credentials"},
    )


async def invalid_token_handler(
    request: Request, exc: InvalidTokenError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc) or "Invalid token"},
    )
