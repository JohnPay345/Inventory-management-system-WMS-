import os
from enum import Enum

from pydantic import Field, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(str, Enum):
  DEVELOPMENT = "development"
  PRODUCTION = "production"


def get_env_file_path() -> str:
  docker_secret = "/run/secrets/app_env_file"
  if os.path.exists(docker_secret):
    return docker_secret

  local_dev = "./.env.development"
  if os.path.exists(local_dev):
    return local_dev

  return "./.env"


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=get_env_file_path(),
    env_file_encoding="utf-8",
    extra="ignore",
  )

  APP_ENV: AppEnv = Field(default=AppEnv.DEVELOPMENT)
  DB_NAME: str = "management_system"
  DB_HOST: str = Field(default="localhost")

  ACCESS_TOKEN: str = Field(default=...)
  REFRESH_TOKEN: str = Field(default=...)
  ACCESS_TOKEN_LIFE: int = Field(default=...)
  REFRESH_TOKEN_LIFE: int = Field(default=...)

  ADMIN_PASSWORD: SecretStr = Field(default=...)
  APP_PASSWORD: SecretStr = Field(default=...)

  @computed_field
  @property
  def DATABASE_URL(self) -> str:
    return f"postgresql+asyncpg://wms_app_user:{self.APP_PASSWORD.get_secret_value()}@{self.DB_HOST}:5432/{self.DB_NAME}"

  @computed_field
  @property
  def ALEMBIC_DATABASE_URL(self) -> str:
    return f"postgresql+psycopg2://admin_db:{self.ADMIN_PASSWORD.get_secret_value()}@{self.DB_HOST}:5432/{self.DB_NAME}"


settings = Settings()
