from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.models.user import User
from app.models.task import Task


class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.task_repository = TaskRepository(self.session)

    async def create_task(self, task_data: TaskCreate, current_user: User) -> Task:
        task = await self.task_repository.create(title=task_data.title, description=task_data.description, deadline=task_data.deadline, owner_id=current_user.id)
        await self.session.commit()
        await self.session.refresh(task)

        return task
    
    async def get_task(self, current_user: User, task_id: int):
        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise ValueError('Task doesn\'t exist!')

        if task.owner_id == current_user.id:
            return task
        else:
            raise PermissionError('User is not permited to get this task.')
    
    async def list_tasks(self, current_user: User):
        tasks = await self.task_repository.list_by_owner_id(current_user.id)
        return tasks
    
    async def delete_task(self, task_id: int, current_user: User):
        task = await self.task_repository.get_by_id(task_id)
        
        if task is None:
            raise ValueError('Task doesn\'t exist!')

        if task.owner_id == current_user.id:
            await self.task_repository.delete(task_id)
            await self.session.commit()
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
            return updated_task
        else:
            raise PermissionError('User is not permitted to update this task.')