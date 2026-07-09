"""Сценарии работы с задачами, кэшем и проверками доступа."""

import json
from datetime import date

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.task import InvalidPaginationError
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.repositories.team_member_repository import TeamMemberRepository
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_permission_service import TaskPermissionService


class TaskService:
    def __init__(self, session: AsyncSession, redis_client: Redis):
        self.session = session
        self.task_repository = TaskRepository(self.session)
        self.team_member_repository = TeamMemberRepository(self.session)
        self.task_permission_service = TaskPermissionService(self.session)
        # Используем один репозиторий в обоих сервисах, чтобы SQL-логика не дублировалась.
        self.task_permission_service.task_repository = self.task_repository
        self.redis_client = redis_client

    async def _invalidate_user_tasks_cache(self, user_id: int) -> None:
        # Удаляем все закэшированные списки задач пользователя после записи.
        pattern = f'tasks:user:{user_id}:*'

        async for key in self.redis_client.scan_iter(match=pattern):
            await self.redis_client.delete(key)

    async def _invalidate_team_tasks_cache(self, team_id: int) -> None:
        # У командных задач нужно сбрасывать кэш у всех участников команды.
        team_members = await self.team_member_repository.list_by_team(team_id)

        for member in team_members:
            await self._invalidate_user_tasks_cache(member.user_id)

    async def _invalidate_accessible_tasks_cache(self, user_id: int, team_id: int | None) -> None:
        await self._invalidate_user_tasks_cache(user_id)

        if team_id is not None:
            await self._invalidate_team_tasks_cache(team_id)

    async def create_task(self, task_data: TaskCreate, current_user: User) -> Task:
        # Если задача создаётся в команде, проверяем, что пользователь в неё входит.
        if task_data.team_id is not None:
            await self.task_permission_service.team_permission_service.ensure_can_view_team(
                team_id=task_data.team_id,
                current_user=current_user,
            )

        task = await self.task_repository.create(
            title=task_data.title,
            description=task_data.description,
            deadline=task_data.deadline,
            owner_id=current_user.id,
            team_id=task_data.team_id,
        )
        await self.session.commit()
        await self.session.refresh(task)

        await self._invalidate_accessible_tasks_cache(current_user.id, task.team_id)
        return task

    async def get_task(self, current_user: User, task_id: int) -> Task:
        # Права доступа и существование задачи проверяются в отдельном сервисе.
        task = await self.task_permission_service.ensure_can_view_task(task_id=task_id, current_user=current_user)
        return task

    async def list_tasks(
        self,
        current_user: User,
        status: TaskStatus | None = None,
        deadline: date | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[dict]:
        # Ограничиваем размер выдачи, чтобы клиент не запросил слишком много строк за раз.
        limit = min(limit, 100)
        if offset < 0 or limit < 0:
            raise InvalidPaginationError('Offset value or limit value is not correct!')

        cache_key = (
            f'tasks:user:{current_user.id}:'
            f'status:{status}:'
            f'deadline:{deadline}:'
            f'limit:{limit}:'
            f'offset:{offset}'
        )
        cached_tasks = await self.redis_client.get(cache_key)

        if cached_tasks is not None:
            return json.loads(cached_tasks)

        tasks = await self.task_repository.list_accessible_by_user(
            user_id=current_user.id,
            status=status,
            deadline=deadline,
            limit=limit,
            offset=offset,
        )

        # Преобразуем ORM-объекты в формат ответа перед записью в кэш.
        tasks = [TaskRead.model_validate(task) for task in tasks]
        tasks_to_dump = [task.model_dump(mode='json') for task in tasks]
        tasks_json = json.dumps(tasks_to_dump)

        await self.redis_client.set(cache_key, tasks_json, ex=60)
        return tasks_to_dump

    async def delete_task(self, task_id: int, current_user: User) -> None:
        # Удаление остаётся доступно только владельцу задачи.
        await self.task_permission_service.ensure_can_delete_task(task_id=task_id, current_user=current_user)

        await self.task_repository.delete(task_id)
        await self.session.commit()

        await self._invalidate_accessible_tasks_cache(current_user.id, task.team_id)

    async def update_task(self, current_user: User, task_id: int, task_updates: TaskUpdate) -> Task:
        # Частичное обновление остаётся доступно только владельцу задачи.
        task = await self.task_permission_service.ensure_can_update_task(task_id=task_id, current_user=current_user)

        updated_task = await self.task_repository.update(task, task_updates)
        await self.session.commit()
        await self.session.refresh(updated_task)

        await self._invalidate_accessible_tasks_cache(current_user.id, task.team_id)
        return updated_task
