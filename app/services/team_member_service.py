from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.team_member_repository import TeamMemberRepository
from app.enums.team_role import TeamRole
from app.models.team_member import TeamMember
from app.models.user import User
from app.exceptions.team_member import TeamMemberAlreadyExistsError, TeamMemberPermissionError, TeamMemberNotFoundError


class TeamMemberService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_member_repository = TeamMemberRepository(session=session)

    async def _get_member_with_management_permission(self, team_id: int, current_user: User) -> TeamMember:
        
        current_member = await self.team_member_repository.get_by_team_and_user(team_id=team_id, user_id=current_user.id)
        
        if current_member is None:
            raise TeamMemberPermissionError("Current user is not a member of this team.")

        if current_member.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise TeamMemberPermissionError('This user is not permitted to create new members in group.')
        
        return current_member

    async def add_member(self, team_id: int, target_user_id: int, role: TeamRole, current_user: User) -> TeamMember:
        
        if role == TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner role cannot be assigned this way.")

        current_member = await self._get_member_with_management_permission(team_id=team_id, current_user=current_user)

        team_member = await self.team_member_repository.get_by_team_and_user(team_id=team_id, user_id=target_user_id)

        if team_member is not None:
            raise TeamMemberAlreadyExistsError('This user is already a team member')

        team_member = await self.team_member_repository.create(team_id=team_id, user_id=target_user_id, role=role)

        await self.session.commit()
        await self.session.refresh(team_member)

        return team_member
    
    async def remove_member(self, team_id: int, target_user_id: int, current_user: User) -> None:

        current_member = await self._get_member_with_management_permission(team_id=team_id, current_user=current_user)
        
        user_to_delete = await self.team_member_repository.get_by_team_and_user(team_id=team_id, user_id=target_user_id)

        if user_to_delete is None:
            raise TeamMemberNotFoundError('Team member doesn\'t exist.')
        
        if user_to_delete.role == TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner cannot be removed from team.")
        
        await self.team_member_repository.delete(user_to_delete)
        await self.session.commit()

    async def change_member_role(self, team_id: int, target_user_id: int, new_role: TeamRole, current_user: User) -> TeamMember:

        if new_role is TeamRole.OWNER:
            raise TeamMemberPermissionError("Owner role cannot be assigned this way.")  

        current_member = await self._get_member_with_management_permission(team_id=team_id, current_user=current_user)

        user_to_change_role = await self.team_member_repository.get_by_team_and_user(team_id=team_id, user_id=target_user_id)

        if user_to_change_role is None:
            raise TeamMemberNotFoundError('Team member doesn\'t exist.')
        
        if user_to_change_role.role == TeamRole.OWNER:
            raise TeamMemberPermissionError('You can not change role of owner.')
        
        
        if user_to_change_role.role == new_role:
            return user_to_change_role

        user_to_change_role = await self.team_member_repository.update_role(user_to_change_role, role=new_role)

        await self.session.commit()
        await self.session.refresh(user_to_change_role)

        return user_to_change_role
    
    async def list_team_members(self, team_id: int, current_user: User) -> list[TeamMember]:

        current_member = await self.team_member_repository.get_by_team_and_user(team_id=team_id, user_id=current_user.id)
        
        if current_member is None:
            raise TeamMemberPermissionError("Current user is not a member of this team.")
        
        team_members = await self.team_member_repository.list_by_team(team_id=team_id)

        return team_members
    
    async def list_my_memberships(self, current_user: User) -> list[TeamMember]:

        memberships = await self.team_member_repository.list_by_user(current_user.id)

        return memberships
        
