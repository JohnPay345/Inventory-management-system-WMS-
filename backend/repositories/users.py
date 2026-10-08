from dataclasses import asdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import NotFoundError
from domain.users import User as UserEntity
from shared.mappers import map_domain_to_orm_flat, map_orm_to_domain_flat
from shared.models import User as UserModel


async def repo_user_exists(db: AsyncSession, username: str) -> UserEntity | None:
  query = select(UserModel).where(UserModel.username == username)
  result = await db.execute(query)
  orm_user = result.scalar_one_or_none()
  if orm_user is None:
    return None
  return map_orm_to_domain_flat(orm_user, UserEntity)


async def repo_get_user_by_id(db: AsyncSession, user_id: UUID) -> UserEntity | None:
  orm_user = await db.get(UserModel, user_id)
  if not orm_user:
    return None
  return map_orm_to_domain_flat(orm_user, UserEntity)


async def repo_user_create(db: AsyncSession, users_data: UserEntity) -> UserEntity:
  orm_user = map_domain_to_orm_flat(users_data, UserModel)
  db.add(orm_user)
  await db.flush()
  await db.refresh(orm_user)
  return map_orm_to_domain_flat(orm_user, UserEntity)


async def repo_user_update(db: AsyncSession, users_data: UserEntity) -> UserEntity:
  orm_user = await db.get(UserModel, users_data.user_id)
  if not orm_user:
    raise NotFoundError(entity_name="User", identifier=str(users_data.user_id))
  values = asdict(users_data)
  values.pop("user_id")
  for key, value in values.items():
    setattr(orm_user, key, value)
  await db.flush()
  return map_orm_to_domain_flat(orm_user, UserEntity)
