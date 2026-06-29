from fastapi import APIRouter, Depends, status

from app.services.dependencies import get_team_member_service
from app.services.dependencies import get_current_user
from app.services.team_member_service import TeamMemberService
from app.schemas.team_member import TeamMemberResponse, AddTeamMember, UpdateTeamMemberRole
from app.enums.team_role import TeamRole
from app.models.user import User


team_member_router = APIRouter(prefix='/teams', tags=['Team Members'])

@team_member_router.post(path='/{team_id}/members', response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_team_member(team_id: int, member_data: AddTeamMember, team_member_service: TeamMemberService = Depends(get_team_member_service), current_user: User = Depends(get_current_user)):
    team_member = await team_member_service.add_member(team_id=team_id, target_user_id=member_data.user_id, role=member_data.role, current_user=current_user)
    return team_member

@team_member_router.get('/{team_id}/members', response_model=list[TeamMemberResponse])
async def get_team_members(team_id: int, team_member_service: TeamMemberService = Depends(get_team_member_service), current_user: User = Depends(get_current_user)):
    team_members = await team_member_service.list_team_members(team_id=team_id, current_user=current_user)
    return team_members

@team_member_router.patch('/{team_id}/members/{user_id}', response_model=TeamMemberResponse)
async def update_team_member(team_id: int, user_id: int, role_data: UpdateTeamMemberRole, team_member_service: TeamMemberService = Depends(get_team_member_service), current_user: User = Depends(get_current_user)):
    updated_team_member = await team_member_service.change_member_role(team_id=team_id, target_user_id=user_id, new_role=role_data.role, current_user=current_user)
    return updated_team_member

@team_member_router.delete('/{team_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(team_id: int, user_id: int, team_member_service: TeamMemberService = Depends(get_team_member_service), current_user: User = Depends(get_current_user)):
    await team_member_service.remove_member(team_id=team_id, target_user_id=user_id, current_user=current_user)
