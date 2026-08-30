from typing import AsyncGenerator
from backend.sevices.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db() -> AsyncGenerator[AsyncSession]:
  async with AsyncSessionLocal() as session:
    yield session
