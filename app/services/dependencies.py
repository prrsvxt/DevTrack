"""Фабрики зависимостей FastAPI для сервисов, сессий и текущего пользователя."""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import bearer_scheme, decode_access_token
from app.db.dependencies import get_session
from app.exceptions.token import InvalidTokenError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.task_service import TaskService
from app.services.team_member_service import TeamMemberService
from app.services.team_service import TeamService
from app.services.user_service import UserService


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CredentialsDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


async def get_redis(request: Request) -> Redis:
    # Redis добавляется в app.state во время старта в main.py.
    return request.app.state.redis


RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_user_service(session: SessionDep, redis_client: RedisDep) -> UserService:
    # Сервис создаётся на каждый запрос, чтобы сессия оставалась request-scoped.
    user_service = UserService(session=session, redis_client=redis_client)
    return user_service


async def get_current_user(session: SessionDep, credentials: CredentialsDep) -> User:
    # Сначала декодируем bearer-токен, затем проверяем, что пользователь существует.
    token = credentials.credentials
    decoded_token = decode_access_token(token)

    try:
        user_id = int(decoded_token["sub"])
    except (KeyError, TypeError, ValueError):
        raise InvalidTokenError("Authentication failed")
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise InvalidTokenError("Authentication failed")

    return user


async def get_task_service(session: SessionDep, redis_client: RedisDep) -> TaskService:
    # TaskService нужны и БД, и кэш для чтения и записи.
    task_service = TaskService(session=session, redis_client=redis_client)
    return task_service


async def get_team_service(session: SessionDep) -> TeamService:
    team_service = TeamService(session)
    return team_service


async def get_team_member_service(session: SessionDep) -> TeamMemberService:
    team_member_service = TeamMemberService(session)
    return team_member_service


CurrentUser = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
TeamServiceDep = Annotated[TeamService, Depends(get_team_service)]
TeamMemberServiceDep = Annotated[TeamMemberService, Depends(get_team_member_service)]
