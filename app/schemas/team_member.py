from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums.team_role import TeamRole


class AddTeamMember(BaseModel):
    user_id: int
    role: TeamRole = TeamRole.DEVELOPER


class UpdateTeamMemberRole(BaseModel):
    role: TeamRole


class TeamMemberResponse(BaseModel):
    id: int
    team_id: int
    user_id: int
    role: TeamRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)
