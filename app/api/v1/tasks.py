"""CRUD-эндпоинты задач, работающие через слой сервиса."""

from fastapi import APIRouter, HTTPException, status
from datetime import date

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models.task import TaskStatus
from app.services.dependencies import CurrentUser, TaskServiceDep


router = APIRouter(prefix='/tasks', tags=['Tasks'])

@router.post('', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, task_service: TaskServiceDep, current_user: CurrentUser):
    # Создание отдаём сервису, чтобы инвалидация кэша выполнялась один раз.
    task = await task_service.create_task(task_data, current_user)
    return task

@router.get('', response_model=list[TaskRead])
async def get_tasks(task_service: TaskServiceDep, current_user: CurrentUser, task_status: TaskStatus | None = None, deadline: date | None = None, limit: int = 10, offset: int = 0):
    # Проверка пагинации и Redis-кэш живут на стороне сервиса.
    tasks = await task_service.list_tasks(current_user=current_user, status=task_status, deadline=deadline, limit=limit, offset=offset)
    return tasks

@router.get('/{task_id}', response_model=TaskRead)
async def get_task_by_id(task_id: int, task_service: TaskServiceDep, current_user: CurrentUser):
    # Проверку существования и прав доступа делает сервис.
    task = await task_service.get_task(current_user, task_id)
    return task

@router.delete('/{task_id}')
async def delete_task_by_id(task_id: int, task_service: TaskServiceDep, current_user: CurrentUser):
    # Удаление ничего не возвращает, а сервис сам поднимает нужные ошибки.
    await task_service.delete_task(task_id, current_user)


@router.patch('/{task_id}', response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskUpdate, task_service: TaskServiceDep, current_user: CurrentUser):
    # Обновление тоже идёт через сервис, чтобы БД и кэш не расходились.
    updated_task = await task_service.update_task(current_user, task_id, task_data)
    
    return updated_task
