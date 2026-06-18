"""Эндпоинты авторизации для регистрации, входа и обновления токенов."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserCreate, UserRead, UserLogin
from app.schemas.tokens import RefreshTokenRequest, TokenRead
from app.models.user import User
from app.services.dependencies import get_user_service, get_current_user
from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    # Ошибки доменной валидации переводим в HTTP 409 для дубликатов.
    try:
        return await user_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.post('/login', response_model=TokenRead)
async def login_user(user_data: UserLogin, user_service: UserService = Depends(get_user_service)):
    # Авторизация остаётся в сервисе, а роут только переводит ошибки в HTTP.
    try:
        user = await user_service.authenticate_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return TokenRead(access_token=access_token, refresh_token=refresh_token)

@router.get('/me', response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    # Dependency FastAPI уже возвращает текущего аутентифицированного пользователя.
    return current_user

@router.post('/refresh', response_model=TokenRead)
async def refresh_token(token_data: RefreshTokenRequest, user_service: UserService = Depends(get_user_service)):
    # Refresh-токен проверяется в сервисе, чтобы роут оставался минимальным.
    access_token, refresh_token = await user_service.rotate_refresh_token(token_data.refresh_token)
    return TokenRead(access_token=access_token, refresh_token=refresh_token)
