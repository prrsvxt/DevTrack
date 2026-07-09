"""Схемы Pydantic для регистрации, входа и чтения пользователя."""

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    # Схема регистрации валидирует данные на границе API.
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    # В ответ наружу отдаём только безопасные поля пользователя.
    id: int
    email: EmailStr
    username: str


class UserLogin(BaseModel):
    # Логин использует ту же пару username/password, что и UI.
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
