from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = Field(default='DevTrack API', alias='APP_NAME')
    debug: bool = Field(default=True, alias='DEBUG')
    database_url: str = Field(alias='DATABASE_URL') 

    jwt_secret_key: str = Field(alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(default='HS256', alias='JWT_ALGORITHM')
    access_token_expire_minutes: int = Field(default=30, alias='ACCESS_TOKEN_EXPIRE_MINUTES')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


settings = Settings()