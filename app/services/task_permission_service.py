"""Проверки прав доступа для операций с задачами."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.team_member import TeamMemberPermissionError
from app.exceptions.task import TaskNotFoundError, TaskPermissionError
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.services.team_permission_service import TeamPermissionService


class TaskPermissionService:
    def __init__(self, session: AsyncSession, task_repository: TaskRepository | None = None, team_permission_service: TeamPermissionService | None = None):
        self.session = session
        self.task_repository = task_repository or TaskRepository(self.session)
        self.team_permission_service = team_permission_service or TeamPermissionService(self.session)

    async def _get_task(self, task_id: int) -> Task:
        task = await self.task_repository.get_by_id(task_id)

        if task is None:
            raise TaskNotFoundError('Task doesn\'t exist!')

        return task

    async def ensure_can_create_task(self, team_id: int | None, current_user: User) -> None:
        # Командные задачи может создавать любой участник команды.
        if team_id is not None:
            await self.team_permission_service.ensure_can_view_team(team_id=team_id, current_user=current_user)

    async def ensure_can_view_task(self, task_id: int, current_user: User) -> Task:
        # Если задача привязана к команде, её могут видеть все участники команды.
        task = await self._get_task(task_id)

        if task.team_id is not None:
            try:
                await self.team_permission_service.ensure_can_view_team(team_id=task.team_id, current_user=current_user)
            except TeamMemberPermissionError as exc:
                raise TaskPermissionError(str(exc)) from exc
            return task

        if task.owner_id != current_user.id:
            raise TaskPermissionError('User is not permited to get this task.')

        return task

    async def ensure_can_update_task(self, task_id: int, current_user: User) -> Task:
        # Обновление остаётся только для владельца задачи.
        task = await self._get_task(task_id)

        if task.owner_id != current_user.id:
            raise TaskPermissionError('User is not permitted to update this task.')

        return task

    async def ensure_can_delete_task(self, task_id: int, current_user: User) -> Task:
        # Удаление остаётся только для владельца задачи.
        task = await self._get_task(task_id)

        if task.owner_id != current_user.id:
            raise TaskPermissionError('User is not permitted to delete this task.')

        return task
