"""Помощники доступа к данным для задач, фильтрации и сохранения."""

from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.team_member import TeamMember
from app.schemas.task import TaskUpdate


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        title: str,
        description: str | None,
        deadline: date | None,
        owner_id: int,
        team_id: int | None = None,
    ) -> Task:
        # ORM-объект собираем здесь, а сервис решает, когда делать commit.
        task = Task(
            title=title,
            description=description,
            deadline=deadline,
            owner_id=owner_id,
            team_id=team_id,
        )
        self.session.add(task)
        return task

    async def get_by_id(self, task_id: int) -> Task | None:
        # Поиск по первичному ключу для просмотра, обновления и удаления.
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_accessible_by_user(
        self,
        user_id: int,
        status=None,
        deadline: date | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Task]:
        # Пользователь видит свои задачи и задачи команд, в которых он состоит.
        stmt = (
            select(Task)
            .outerjoin(TeamMember, Task.team_id == TeamMember.team_id)
            .where(or_(Task.owner_id == user_id, TeamMember.user_id == user_id))
            .distinct()
        )

        if status is not None:
            stmt = stmt.where(Task.status == status)

        if deadline is not None:
            stmt = stmt.where(Task.deadline == deadline)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, task_id: int) -> None:
        # Удаление выполняется после того, как сервис подтвердил права доступа.
        task_for_delete = await self.get_by_id(task_id)
        await self.session.delete(task_for_delete)

    async def update(self, task: Task, task_data: TaskUpdate) -> Task:
        # Применяем только те поля, которые реально прислал клиент.
        updates = task_data.model_dump(exclude_unset=True)

        for field_name, value in updates.items():
            setattr(task, field_name, value)

        return task
