from typing import Protocol
from uuid import UUID

from domain.exceptions import AlreadyExistsError, LoginFailedError
from domain.users import User as UserEntity
from services.tokens import generate_token
from shared.schemas import LoginRequest, RegisterRequest, TokenPayload


class UserProtocol(Protocol):
  async def repo_user_exists(self, username: str) -> UserEntity | None: ...
  async def repo_get_user_by_id(self, user_id: UUID) -> UserEntity | None: ...
  async def repo_user_create(self, users_data: UserEntity) -> UserEntity: ...
  async def repo_user_update(self, users_data: UserEntity) -> UserEntity: ...


async def case_login(users_data: LoginRequest, repository: UserProtocol) -> dict[str, str]:
  is_user = await repository.repo_user_exists(users_data.username)
  if is_user is None:
    raise LoginFailedError(entity_name="User")
  if not is_user.check_password(users_data.password):
    raise LoginFailedError(entity_name="User")
  tokens = generate_token(is_user.username, str(is_user.user_id), [is_user.role])
  return tokens


async def case_register(users_data: RegisterRequest, repository: UserProtocol) -> UserEntity:
  is_user = await repository.repo_user_exists(users_data.username)
  if is_user:
    raise AlreadyExistsError(entity_name="User", conflict_details=users_data.username)
  user_entity = UserEntity.create(
    users_data.first_name,
    users_data.middle_name,
    users_data.last_name,
    users_data.username,
    users_data.password,
    users_data.role,
  )
  new_user = await repository.repo_user_create(user_entity)
  return new_user


async def case_update_tokens(refresh_token: TokenPayload):
  user_id, username, role = refresh_token.model_dump()
  tokens = generate_token(username, user_id, list(role))
  return tokens
