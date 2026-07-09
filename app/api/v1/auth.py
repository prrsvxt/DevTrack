"""Эндпоинты авторизации для регистрации, входа и обновления токенов."""

from fastapi import APIRouter, status

from app.core.security import create_access_token, create_refresh_token
from app.schemas.tokens import RefreshTokenRequest, TokenRead
from app.schemas.user import UserCreate, UserLogin, UserRead
from app.services.dependencies import CurrentUser, UserServiceDep


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_service: UserServiceDep) -> UserRead:
    user = await user_service.register_user(user_data)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenRead)
async def login_user(user_data: UserLogin, user_service: UserServiceDep):
    user = await user_service.authenticate_user(user_data)

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return TokenRead(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:
    # Dependency FastAPI уже возвращает текущего аутентифицированного пользователя.
    return UserRead.model_validate(current_user)


@router.post("/refresh", response_model=TokenRead)
async def refresh_token(token_data: RefreshTokenRequest, user_service: UserServiceDep):
    # Refresh-токен проверяется в сервисе, чтобы роут оставался минимальным.
    access_token, refresh_token = await user_service.rotate_refresh_token(
        token_data.refresh_token
    )
    return TokenRead(access_token=access_token, refresh_token=refresh_token)
