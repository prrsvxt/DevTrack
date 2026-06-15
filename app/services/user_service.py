from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> User:
        existing_user_by_email = await self.user_repository.get_by_email(user_data.email)

        if existing_user_by_email is not None:
            raise ValueError('User with this email already exists')
        
        existing_user_by_username = await self.user_repository.get_by_username(user_data.username)

        if existing_user_by_username is not None:
            raise ValueError('This username is already taken')
        
        hashed_password = hash_password(user_data.password)

        user = await self.user_repository.create(email=user_data.email, username=user_data.username, hashed_password=hashed_password)
        await self.session.commit()
        await self.session.refresh(user)

        return user
    
    async def authenticate_user(self, user_data: UserLogin) -> User:
        user = await self.user_repository.get_by_username(user_data.username)

        if user is None:
            raise ValueError('Invalid username or password')
        
        if not verify_password(user_data.password, user.hashed_password):
            raise ValueError('Invalid username or password')
        
        return user