from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models.user import User
from app.models.task import TaskStatus
from app.services.task_service import TaskService
from app.services.dependencies import get_task_service, get_current_user


router = APIRouter(prefix='/tasks', tags=['Tasks'])

@router.post('', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    task = await task_service.create_task(task_data, current_user)
    return task

@router.get('', response_model=list[TaskRead])
async def get_tasks(status: TaskStatus | None = None, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    tasks = await task_service.list_tasks(current_user=current_user, status=status)
    return tasks

@router.get('/{task_id}', response_model=TaskRead)
async def get_task_by_id(task_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        task = await task_service.get_task(current_user, task_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return task

@router.delete('/{task_id}')
async def delete_task_by_id(task_id: int, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        await task_service.delete_task(task_id, current_user)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Action Forbidden.')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task is not found.')


@router.patch('/{task_id}', response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskUpdate, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    try:
        updated_task = await task_service.update_task(current_user, task_id, task_data)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Action Forbidden.')
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task is not found.')
    
    return updated_task