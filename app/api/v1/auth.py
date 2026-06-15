from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.user import UserCreate, UserRead, UserLogin, TokenRead
from app.services.dependencies import get_user_service
from app.services.user_service import UserService
from app.core.security import create_access_token


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    try:
        return await user_service.register_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
@router.post('/login', response_model=TokenRead)
async def login_user(user_data: UserLogin, user_service: UserService = Depends(get_user_service)):
    try:
        user = await user_service.authenticate_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    access_token = create_access_token(subject=str(user.id))
    return TokenRead(access_token=access_token)
    