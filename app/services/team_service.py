from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.team_role import TeamRole
from app.exceptions.team import TeamNotFoundError
from app.models.team import Team
from app.models.user import User
from app.repositories.team_member_repository import TeamMemberRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.team import CreateTeam, UpdateTeam
from app.services.team_permission_service import TeamPermissionService


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repository = TeamRepository(self.session)
        self.team_member_repository = TeamMemberRepository(self.session)
        self.team_permission_service = TeamPermissionService(
            self.session, team_member_repository=self.team_member_repository
        )

    async def create_team(self, current_user: User, team_data: CreateTeam) -> Team:
        owner_id = current_user.id

        team = await self.team_repository.create(
            team_data.name, team_data.description, owner_id
        )

        await self.session.flush()

        await self.team_member_repository.create(
            team_id=team.id, user_id=owner_id, role=TeamRole.OWNER
        )

        await self.session.commit()
        await self.session.refresh(team)

        return team

    async def get_team(self, current_user: User, team_id: int) -> Team:
        await self.team_permission_service.ensure_can_view_team(
            team_id=team_id, current_user=current_user
        )

        team = await self.team_repository.get_by_id(team_id=team_id)
        if team is None:
            raise TeamNotFoundError("Team doesn't exist!")
        return team

    async def get_my_teams(self, current_user: User) -> list[Team]:
        teams = await self.team_repository.get_by_member_user_id(current_user.id)
        return teams

    async def update_team(
        self, current_user: User, team_id: int, team_updates: UpdateTeam
    ) -> Team:
        await self.team_permission_service.ensure_can_update_team(
            team_id=team_id, current_user=current_user
        )

        team = await self.team_repository.get_by_id(team_id=team_id)
        if team is None:
            raise TeamNotFoundError("Team doesn't exist!")

        updated_team = await self.team_repository.update(team, team_updates)
        await self.session.commit()
        await self.session.refresh(updated_team)

        return updated_team

    async def delete_team(self, current_user: User, team_id: int) -> None:
        await self.team_permission_service.ensure_can_delete_team(
            team_id=team_id, current_user=current_user
        )

        team_to_delete = await self.team_repository.get_by_id(team_id=team_id)
        if team_to_delete is None:
            raise TeamNotFoundError("Team doesn't exist!")

        await self.team_repository.delete(team_to_delete)
        await self.session.commit()
