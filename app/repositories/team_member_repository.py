from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.team_member import TeamMember
from app.enums.team_role import TeamRole


class TeamMemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, team_id: int, user_id: int, role: TeamRole) -> TeamMember:
        team_member = TeamMember(team_id=team_id, user_id=user_id, role=role)
        self.session.add(team_member)
        return team_member

    async def get_by_team_and_user(
        self, team_id: int, user_id: int
    ) -> TeamMember | None:
        stmt = select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, member_id: int) -> TeamMember | None:
        stmt = select(TeamMember).where(TeamMember.id == member_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_team(self, team_id: int) -> list[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.team_id == team_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int) -> list[TeamMember]:
        stmt = select(TeamMember).where(TeamMember.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_role(self, member: TeamMember, role: TeamRole) -> TeamMember:
        member.role = role
        return member

    async def delete(self, team_member: TeamMember) -> None:
        await self.session.delete(team_member)
