from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from shared.config import settings

engine = create_async_engine(
  settings.DATABASE_URL,
  connect_args={"server_settings": {"search_path": "app_schema"}},
)

AsyncSessionLocal = async_sessionmaker(
  autocommit=False, autoflush=False, class_=AsyncSession, bind=engine
)


class Base(DeclarativeBase):
  metadata = MetaData(schema="app_schema")
