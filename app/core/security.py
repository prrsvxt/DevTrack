"""Хелперы для хэширования паролей и работы с JWT."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from fastapi.security import HTTPBearer
from pwdlib import PasswordHash

from app.core.config import settings
from app.exceptions.token import InvalidTokenError


password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    # Хэширование пароля централизовано, чтобы алгоритм было легко заменить.
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Проверка пароля использует тот же механизм, что и хэширование.
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    # Access-токены короткоживущие и содержат только id пользователя и тип.
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        'sub': subject,
        'exp': expires_at,
        'type': 'access',
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    # Невалидный или истёкший JWT преобразуем в доменное исключение.
    try:
        decoded_token = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as e:
        raise InvalidTokenError('Invalid token') from e
    return decoded_token


def create_refresh_token(subject: str) -> str:
    # Refresh-токен живёт дольше и содержит JTI для будущей ревокации.
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    payload = {
        'sub': subject,
        'exp': expires_at,
        'type': 'refresh',
        'jti': str(uuid4()),
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
