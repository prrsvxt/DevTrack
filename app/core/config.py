"""Типизированные настройки, загружаемые из окружения и .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Значения по умолчанию близки к имени приложения и локальной разработке.
    app_name: str = Field(default="DevTrack API", alias="APP_NAME")
    debug: bool = Field(default=True, alias="DEBUG")
    database_url: str = Field(alias="DATABASE_URL")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    refresh_token_expire_days: int = 7

    redis_host: str
    redis_port: int
    redis_password: str
    redis_db: int

    smtp_host: str
    smtp_port: int
    email_from: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
