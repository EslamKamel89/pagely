import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_EXPIRE_MINUTES: int
    REFRESH_EXPIRE_DAYS: int
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # type: ignore
