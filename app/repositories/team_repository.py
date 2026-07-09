from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team
from app.schemas.team import UpdateTeam
from app.models.team_member import TeamMember


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, description: str | None, owner_id: int) -> Team:
        team = Team(name=name, description=description, owner_id=owner_id)
        self.session.add(team)
        return team

    async def get_by_id(self, team_id: int) -> Team | None:
        stmt = select(Team).where(Team.id == team_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_owned_by_user(self, owner_id) -> list[Team]:
        stmt = select(Team).where(Team.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_member_user_id(self, user_id: int) -> list[Team]:
        stmt = select(Team).join(Team.team_members).where(TeamMember.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalars.all()
    
    async def update(self, team: Team, team_data: UpdateTeam) -> Team:
        update_data = team_data.model_dump(exclude_unset=True)

        for field_name, value in update_data.values():
            setattr(team, field_name, value)
        
        return team
    
    async def delete(self, team: Team) -> None: 
        await self.session.delete(team)