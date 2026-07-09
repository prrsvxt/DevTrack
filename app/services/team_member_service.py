"""Бизнес-логика для управления участниками команд."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.team_role import TeamRole
from app.exceptions.team_member import (
    TeamMemberAlreadyExistsError,
    TeamMemberNotFoundError,
    TeamMemberPermissionError,
)
from app.models.team_member import TeamMember
from app.models.user import User
from app.repositories.team_member_repository import TeamMemberRepository
from app.services.team_permission_service import TeamPermissionService


class TeamMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_member_repository = TeamMemberRepository(session=session)
        self.team_permission_service = TeamPermissionService(
            session, team_member_repository=self.team_member_repository
        )

    async def _get_team_member(self, team_id: int, user_id: int) -> TeamMember:
        team_member = await self.team_member_repository.get_by_team_and_user(
            team_id=team_id, user_id=user_id
        )

        if team_member is None:
            raise TeamMemberNotFoundError("Team member doesn't exist.")

        return team_member

    async def add_member(
        self, team_id: int, target_user_id: int, role: TeamRole, current_user: User
    ) -> TeamMember:
        # Владельца нельзя назначить через обычный flow добавления.
        if role == TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner role cannot be assigned this way.")

        # Управлять участниками могут только владелец и администратор.
        await self.team_permission_service.ensure_can_manage_members(
            team_id=team_id, current_user=current_user
        )

        team_member = await self.team_member_repository.get_by_team_and_user(
            team_id=team_id, user_id=target_user_id
        )

        if team_member is not None:
            raise TeamMemberAlreadyExistsError("This user is already a team member")

        team_member = await self.team_member_repository.create(
            team_id=team_id, user_id=target_user_id, role=role
        )

        await self.session.commit()
        await self.session.refresh(team_member)

        return team_member

    async def remove_member(
        self, team_id: int, target_user_id: int, current_user: User
    ) -> None:
        # Удаление участников тоже доступно только управляющим ролям.
        await self.team_permission_service.ensure_can_manage_members(
            team_id=team_id, current_user=current_user
        )

        user_to_delete = await self._get_team_member(
            team_id=team_id, user_id=target_user_id
        )

        if user_to_delete.role == TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner cannot be removed from team.")

        await self.team_member_repository.delete(user_to_delete)
        await self.session.commit()

    async def change_member_role(
        self, team_id: int, target_user_id: int, new_role: TeamRole, current_user: User
    ) -> TeamMember:
        # Владельца нельзя назначить через смену роли.
        if new_role is TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner role cannot be assigned this way.")

        await self.team_permission_service.ensure_can_manage_members(
            team_id=team_id, current_user=current_user
        )

        user_to_change_role = await self._get_team_member(
            team_id=team_id, user_id=target_user_id
        )

        if user_to_change_role.role == TeamRole.OWNER:
            raise TeamMemberPermissionError("You can not change role of owner.")

        if user_to_change_role.role == new_role:
            return user_to_change_role

        user_to_change_role = await self.team_member_repository.update_role(
            user_to_change_role, role=new_role
        )

        await self.session.commit()
        await self.session.refresh(user_to_change_role)

        return user_to_change_role

    async def list_team_members(
        self, team_id: int, current_user: User
    ) -> list[TeamMember]:
        # Список участников виден только тем, кто уже состоит в команде.
        await self.team_permission_service.ensure_can_view_team(
            team_id=team_id, current_user=current_user
        )

        team_members = await self.team_member_repository.list_by_team(team_id=team_id)

        return team_members

    async def list_my_memberships(self, current_user: User) -> list[TeamMember]:
        memberships = await self.team_member_repository.list_by_user(current_user.id)

        return memberships
