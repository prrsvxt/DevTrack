from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.team_repository import TeamRepository
from app.repositories.team_member_repository import TeamMemberRepository
from app.services.team_member_service import TeamMemberService
from app.services.team_permission_service import TeamPermissionService
from app.schemas.team import UpdateTeam, CreateTeam
from app.enums.team_role import TeamRole
from app.models.team import Team
from app.models.user import User


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repository = TeamRepository(self.session)
        self.team_member_repository = TeamMemberRepository(self.session)
        self.team_member_service = TeamMemberService(self.session)
        self.team_permission_service = TeamPermissionService(self.session)

    # create_team
    async def create_team(self, current_user: User, team_data: CreateTeam) -> Team:
        owner_id = current_user.id
        
        team = await self.team_repository.create(team_data.name, team_data.description, owner_id)

        await self.session.flush()

        await self.team_member_repository.create(team_id=team.id, user_id=owner_id, role=TeamRole.OWNER)

        await self.session.commit()
        await self.session.refresh(team)

        return team

    # get_team
    async def get_team(self, current_user: User, team_id: int) -> Team:
        await self.team_permission_service.ensure_can_view_team(team_id=team_id, current_user=current_user)

        team = await self.team_repository.get_by_id(team_id=team_id)
        return team
    
    # get_my_teams
    async def get_my_teams(self, current_user: User) -> list[Team]:
        teams = await self.team_repository.get_by_member_user_id(current_user.id)
        return teams
    
    # update_team 
    async def update_team(self, current_user: User, team_id: int, team_updates: UpdateTeam) -> Team:
        
        await self.team_permission_service.ensure_can_update_team(team_id=team_id, current_user=current_user)

        team = await self.team_repository.get_by_id(team_id=team_id)
        
        updated_team = await self.team_repository.update(team, team_updates)
        await self.session.commit()
        await self.session.refresh(updated_team)

        return updated_team
    
    # delete_team
    async def delete_team(self, current_user: User, team_id: int) -> None:
        
        await self.team_permission_service.ensure_can_delete_team(team_id=team_id, current_user=current_user)

        team_to_delete = await self.team_repository.get_by_id(team_id=team_id)

        await self.team_repository.delete(team_to_delete)
        await self.session.commit()

