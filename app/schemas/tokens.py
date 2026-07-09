"""Схемы Pydantic для запросов и ответов с токенами."""

from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    # Refresh-токен передаётся в теле запроса.
    refresh_token: str


class TokenRead(BaseModel):
    # После логина возвращаем и access, и refresh токен.
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
