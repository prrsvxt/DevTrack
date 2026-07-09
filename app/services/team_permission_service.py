from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.team_role import TeamRole
from app.exceptions.team_member import TeamMemberPermissionError
from app.models.team_member import TeamMember
from app.models.user import User
from app.repositories.team_member_repository import TeamMemberRepository


class TeamPermissionService:
    UPDATE_TEAM_ROLES = {TeamRole.OWNER, TeamRole.ADMIN}
    MANAGE_MEMBERS_ROLES = {TeamRole.OWNER, TeamRole.ADMIN}
    DELETE_TEAM_ROLES = {TeamRole.OWNER}

    def __init__(
        self,
        session: AsyncSession,
        team_member_repository: TeamMemberRepository | None = None,
    ):
        self.session = session
        self.team_member_repository = team_member_repository or TeamMemberRepository(
            self.session
        )

    async def ensure_can_view_team(
        self, team_id: int, current_user: User
    ) -> TeamMember:
        team_member = await self.team_member_repository.get_by_team_and_user(
            team_id=team_id, user_id=current_user.id
        )

        if team_member is None:
            raise TeamMemberPermissionError(
                "This user is not permitted to view this team"
            )

        return team_member

    async def ensure_can_update_team(
        self, team_id: int, current_user: User
    ) -> TeamMember:
        team_member = await self.ensure_can_view_team(
            team_id=team_id, current_user=current_user
        )

        if team_member.role not in self.UPDATE_TEAM_ROLES:
            raise TeamMemberPermissionError(
                "This user is not permitted to solve this action"
            )

        return team_member

    async def ensure_can_delete_team(
        self, team_id: int, current_user: User
    ) -> TeamMember:
        team_member = await self.ensure_can_view_team(
            team_id=team_id, current_user=current_user
        )

        if team_member.role not in self.DELETE_TEAM_ROLES:
            raise TeamMemberPermissionError(
                "This user is not permitted to solve this action"
            )

        return team_member

    async def ensure_can_manage_members(
        self, team_id: int, current_user: User
    ) -> TeamMember:
        team_member = await self.ensure_can_view_team(
            team_id=team_id, current_user=current_user
        )

        if team_member.role not in self.MANAGE_MEMBERS_ROLES:
            raise TeamMemberPermissionError(
                "This user is not permitted to solve this action"
            )

        return team_member
