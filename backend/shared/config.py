import os
from dotenv import load_dotenv


env_file = "/run/secrets/app_env_file"
if os.path.exists(env_file):
  load_dotenv(env_file)
elif os.path.exists("./.env.developemnt"):
  load_dotenv("./.env.developemnt")


class Settings:
  def __init__(self, APP_ENV, DB_HOST, ADMIN_PASSWORD, APP_PASSWORD):
    self.APP_ENV = APP_ENV
    self.DB_NAME = "management_system"
    self.DB_HOST = DB_HOST

    # Читаем секреты из файлов (подходит и для Docker Secrets, и для локальной разработки)
    self.ADMIN_PASSWORD = ADMIN_PASSWORD
    self.APP_PASSWORD = APP_PASSWORD

  @property
  def DATABASE_URL(self):
    return (
      f"postgresql+asyncpg://wms_app_user:{self.APP_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"
    )

  @property
  def ALEMBIC_DATABASE_URL(self):
    return (
      f"postgresql+psycopg2://admin_db:{self.ADMIN_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"
    )


settings = Settings(
  APP_ENV=os.getenv("APP_ENV", "development"),
  DB_HOST=os.getenv("DB_HOST", "localhost"),
  ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD"),
  APP_PASSWORD=os.getenv("APP_PASSWORD"),
)
