from fastapi import APIRouter, status

from app.services.dependencies import CurrentUser, TeamServiceDep
from app.schemas.team import TeamResponse, CreateTeam, UpdateTeam

team_router = APIRouter(prefix='/teams', tags=['Teams'])

@team_router.post('/', response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(team_data: CreateTeam, current_user: CurrentUser, team_service: TeamServiceDep):
    team = await team_service.create_team(current_user=current_user, team_data=team_data)
    return team

@team_router.get('/my', response_model=list[TeamResponse])
async def get_my_teams(current_user: CurrentUser, team_service: TeamServiceDep):
    teams = await team_service.get_my_teams(current_user=current_user)
    return teams

@team_router.get('/{team_id}', response_model=TeamResponse)
async def get_team_by_id(team_id: int, current_user: CurrentUser, team_service: TeamServiceDep):
    team = await team_service.get_team(current_user=current_user, team_id=team_id)
    return team

@team_router.patch('/{team_id}', response_model=TeamResponse)
async def update_team(team_id: int, team_updates: UpdateTeam, current_user: CurrentUser, team_service: TeamServiceDep):
    updated_team = await team_service.update_team(current_user=current_user, team_id=team_id, team_updates=team_updates)
    return updated_team

@team_router.delete('/{team_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, current_user: CurrentUser, team_service: TeamServiceDep):
    await team_service.delete_team(current_user=current_user, team_id=team_id)
