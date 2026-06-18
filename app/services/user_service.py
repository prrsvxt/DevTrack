"""Бизнес-логика регистрации, авторизации и обновления токенов."""

from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from datetime import datetime, timezone

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token, create_refresh_token
from app.core.config import settings
from app.exceptions.token import TokenBlacklistedError


class UserService:
    def __init__(self, session: AsyncSession, redis_client: Redis):
        self.session = session
        self.user_repository = UserRepository(session)
        self.redis_client = redis_client

    async def register_user(self, user_data: UserCreate) -> User:
        # Проверяем дубликаты до хэширования, чтобы быстрее вернуть конфликт.
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
        # Возвращаем одинаковую ошибку для обоих случаев, чтобы не подсказывать лишнее.
        user = await self.user_repository.get_by_username(user_data.username)

        if user is None:
            raise ValueError('Invalid username or password')
        
        if not verify_password(user_data.password, user.hashed_password):
            raise ValueError('Invalid username or password')
        
        return user
    
    async def rotate_refresh_token(self, refresh_token: str):
        # Refresh-токен сначала декодируется, а потом сверяется с хранилищем.
        decoded_token = decode_access_token(refresh_token)
        user_id = decoded_token.get('sub')
        if decoded_token.get('type') != 'refresh':
            raise ValueError('Invalid token.')
        
        token_jti = decoded_token.get('jti')
        token_exp = decoded_token.get('exp')
        
        if token_jti is None:
            raise ValueError('Token not found.')
        
        if token_exp is None:
            raise ValueError("Token exp not found.")
        
        cache_key = f'refresh:blacklist:{token_jti}'
        
        token_blacklisted = await self.redis_client.get(cache_key)
        if token_blacklisted:
            raise TokenBlacklistedError('Token is blacklisted')
        
        user = await self.user_repository.get_by_id(int(user_id))
        if user is None:
            raise ValueError('Access Denied.')

        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)

        now = datetime.now(timezone.utc).timestamp()
        ttl = int(token_exp - now)

        if ttl <= 0:
            raise ValueError("Token expired.")

        await self.redis_client.set(cache_key, 'revoked', ex=ttl)
        return access_token, refresh_token
