from fastapi import APIRouter, HTTPException, Depends, status

from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models.user import User
from app.services.task_service import TaskService
from app.services.dependencies import get_task_service, get_current_user


router = APIRouter(prefix='/tasks', tags=['Tasks'])

@router.post('', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, task_service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    task = await task_service.create_task(task_data, current_user)
    return task
