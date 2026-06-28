from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.team_repository import TeamRepository
from app.schemas.team import UpdateTeam, CreateTeam
from app.exceptions.team import TeamNotFoundError, TeamPermissionError
from app.models.team import Team
from app.models.user import User


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repository = TeamRepository(self.session)
    
    async def _get_owned_team(self, team_id: int, current_user: User) -> Team:
        team = await self.team_repository.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError("Team not found.")
        if current_user.id != team.owner_id:
            raise TeamPermissionError("You do not have permission to access this team.")
        return team

    # create_team
    async def create_team(self, current_user: User, team_data: CreateTeam) -> Team:
        owner_id = current_user.id

        team = await self.team_repository.create(team_data.name, team_data.description, owner_id)
        await self.session.commit()
        await self.session.refresh(team)

        return team

    # get_team
    async def get_team(self, current_user: User, team_id: int) -> Team:
        team = await self._get_owned_team(team_id, current_user)
        return team
    
    # get_my_teams
    async def get_my_teams(self, current_user: User) -> list[Team]:
        teams = await self.team_repository.get_owned_by_user(current_user.id)
        return teams
    
    # update_team
    async def update_team(self, current_user: User, team_id: int, team_updates: UpdateTeam) -> Team:
        team = await self._get_owned_team(team_id, current_user)
        
        updated_team = await self.team_repository.update(team, team_updates)
        await self.session.commit()
        await self.session.refresh(updated_team)

        return updated_team
    
    # delete_team
    async def delete_team(self, current_user: User, team_id: int) -> None:
        team_to_delete = await self._get_owned_team(team_id, current_user)
        
        await self.team_repository.delete(team_to_delete)
        await self.session.commit()

