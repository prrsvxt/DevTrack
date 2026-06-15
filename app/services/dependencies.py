from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.services.user_service import UserService
from app.db.dependencies import get_session
from app.core.security import oauth2_scheme, decode_access_token
from app.repositories.user_repository import UserRepository

async def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    
    user_service = UserService(session=session)
    return user_service

async def get_current_user(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme)):
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
