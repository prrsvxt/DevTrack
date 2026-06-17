from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from redis.asyncio import Redis
import json

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models.user import User
from app.models.task import Task


class TaskService:
    def __init__(self, session: AsyncSession, redis_client: Redis):
        self.session = session
        self.task_repository = TaskRepository(self.session)
        self.redis_client = redis_client

    async def _invalidate_user_tasks_cache(self, user_id: int):
        pattern = f'tasks:user:{user_id}:*'

        async for key in self.redis_client.scan_iter(match=pattern):
            await self.redis_client.delete(key)

    async def create_task(self, task_data: TaskCreate, current_user: User) -> Task:
        task = await self.task_repository.create(title=task_data.title, description=task_data.description, deadline=task_data.deadline, owner_id=current_user.id)
        await self.session.commit()
        await self.session.refresh(task)

        await self._invalidate_user_tasks_cache(current_user.id)
        return task
    
    async def get_task(self, current_user: User, task_id: int):
        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise ValueError('Task doesn\'t exist!')

        if task.owner_id == current_user.id:
            return task
        else:
            raise PermissionError('User is not permited to get this task.')
    
    async def list_tasks(self, current_user: User, status=None, deadline: date | None = None, limit: int = 10, offset: int = 0):

        limit = min(limit, 100)
        if offset < 0 or limit < 0 :
            raise ValueError('Offset value or limit value is not correct!')
        
        cache_key = (
            f"tasks:user:{current_user.id}:"
            f"status:{status}:"
            f"deadline:{deadline}:"
            f"limit:{limit}:"
            f"offset:{offset}"
        )
        cached_tasks = await self.redis_client.get(cache_key)
        
        if cached_tasks is not None:
            return json.loads(cached_tasks)
        
        tasks = await self.task_repository.list_by_owner_id(current_user.id, status, deadline, limit, offset)
        
        tasks = [TaskRead.model_validate(task) for task in tasks]
        tasks_to_dump = [task.model_dump(mode='json') for task in tasks]
        tasks_json = json.dumps(tasks_to_dump)

        await self.redis_client.set(cache_key, tasks_json, ex=60)
        return tasks_to_dump
    
    async def delete_task(self, task_id: int, current_user: User):
        task = await self.task_repository.get_by_id(task_id)
        
        if task is None:
            raise ValueError('Task doesn\'t exist!')

        if task.owner_id == current_user.id:
            await self.task_repository.delete(task_id)
            await self.session.commit()

            await self._invalidate_user_tasks_cache(current_user.id)
            return None
        else:
            raise PermissionError('User is not permitted to delete this task.')
    
    async def update_task(self, current_user: User, task_id: int , task_updates: TaskUpdate):

        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise ValueError('Task doesn\'t exist!')

        if current_user.id == task.owner_id:
            updated_task = await self.task_repository.update(task, task_updates)
            await self.session.commit()
            await self.session.refresh(updated_task)

            await self._invalidate_user_tasks_cache(current_user.id)
            return updated_task
        else:
            raise PermissionError('User is not permitted to update this task.')