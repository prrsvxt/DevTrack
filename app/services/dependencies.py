"""Фабрики зависимостей FastAPI для сервисов, сессий и текущего пользователя."""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status, Request
from redis.asyncio import Redis
from fastapi.security import HTTPAuthorizationCredentials

from app.services.user_service import UserService
from app.services.task_service import TaskService
from app.db.dependencies import get_session
from app.core.security import bearer_scheme, decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import User

async def get_redis(request: Request) -> Redis:
    # Redis добавляется в app.state во время старта в main.py.
    return request.app.state.redis

async def get_user_service(session: AsyncSession = Depends(get_session), redis_client: Redis = Depends(get_redis)) -> UserService:
    # Сервис создаётся на каждый запрос, чтобы сессия оставалась request-scoped.
    user_service = UserService(session=session, redis_client=redis_client)
    return user_service

async def get_current_user(session: AsyncSession = Depends(get_session), credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    # Сначала декодируем bearer-токен, затем проверяем, что пользователь существует.
    token = credentials.credentials
    try:
        decoded_token = decode_access_token(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    
    try:
        user_id = int(decoded_token['sub'])
    except (KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    
    return user

async def get_task_service(session: AsyncSession = Depends(get_session), redis_client: Redis = Depends(get_redis)) -> TaskService:
    # TaskService нужны и БД, и кэш для чтения и записи.
    task_service = TaskService(session=session, redis_client=redis_client)
    return task_service
