"""Обработчики исключений FastAPI, возвращающие единый JSON-формат."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions.task import TaskNotFoundError, TaskPermissionError, InvalidPaginationError


async def task_not_found_handler(request: Request, exc:TaskNotFoundError) -> JSONResponse:
    # Все ошибки отсутствия задачи приводим к одному JSON-ответу.
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "not found"})

async def task_permission_handler(request: Request, exc: TaskPermissionError) -> JSONResponse:
    # Ошибку прав доступа отделяем от ошибки отсутствия ресурса.
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You do not have permission to access this task"})

async def invalid_pagination_handler(request: Request, exc: InvalidPaginationError) -> JSONResponse:
    # Неверная пагинация - это ошибка клиента, поэтому отдаём HTTP 400.
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Bad pagination params"})

