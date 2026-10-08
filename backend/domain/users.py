from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import bcrypt

from domain.exceptions import BusinessRuleViolationError
from shared.enum import UserRole


@dataclass
class User:
  user_id: UUID | None
  first_name: str
  middle_name: str
  username: str
  password_hash: str
  role: UserRole
  created_at: datetime
  last_name: str | None = ""
  is_active: bool = True

  @classmethod
  def create(
    cls,
    first_name: str,
    middle_name: str,
    last_name: str | None,
    username: str,
    password: str,
    role: UserRole,
  ) -> "User":
    if not (first_name or middle_name or username or password or role):
      raise BusinessRuleViolationError(
        entity_name="User", identifier="-", conflict_details="Нужные поля отсутствуют"
      )
    if not UserRole(role):
      raise BusinessRuleViolationError(
        entity_name="User", identifier="-", conflict_details="Роль не соответствует списку"
      )
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    return cls(
      user_id=uuid4(),
      first_name=first_name,
      middle_name=middle_name,
      last_name=last_name,
      username=username,
      password_hash=password_hash,
      role=role,
      is_active=True,
      created_at=datetime.now(UTC),
    )

  def update(self, changes) -> "User":
    if "user_id" in changes or "created_at" in changes:
      raise BusinessRuleViolationError(
        entity_name="User",
        identifier=str(self.user_id),
        conflict_details="Нельзя изменять системные поля",
      )
    updated_entity = replace(self, **changes)
    updated_entity._validate()
    return updated_entity

  def check_password(self, password_hash: str) -> bool:
    return bcrypt.checkpw(password_hash.encode("utf-8"), self.password_hash.encode("utf-8"))

  def _validate(self):
    if not (self.first_name or self.middle_name or self.username or self.password_hash):
      raise BusinessRuleViolationError(
        entity_name="User",
        identifier=str(self.user_id),
        conflict_details="Поля не могут быть пустыми",
      )
