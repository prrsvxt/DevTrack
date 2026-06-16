from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.task import Task
from app.schemas.task import TaskUpdate


class TaskRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, title: str, description: str, deadline: datetime, owner_id: int):
        task = Task(title=title, description=description, deadline=deadline, owner_id=owner_id)
        self.session.add(task)
        return task
    
    async def get_by_id(self, task_id: int):
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_owner_id(self, owner_id: int):
        stmt = select(Task).where(Task.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, task_id: int):
        task_for_delete = await self.get_by_id(task_id)
        await self.session.delete(task_for_delete)

    async def update(self, task: Task, task_data: TaskUpdate) -> Task:
        updates = task_data.model_dump(exclude_unset=True)

        for field_name, value in updates.items():
            setattr(task, field_name, value)
        
        return task
