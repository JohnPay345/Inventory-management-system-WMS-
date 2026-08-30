from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from backend.shared.config import settings

load_dotenv()

engine = create_async_engine(
  settings.DATABASE_URL,
  connect_args={"check_same_thread": False, "options": "-csearch_path=app_schema"},
)

AsyncSessionLocal = async_sessionmaker(
  autocommit=False, autoflush=False, class_=AsyncSession, bind=engine
)

Base = declarative_base()
