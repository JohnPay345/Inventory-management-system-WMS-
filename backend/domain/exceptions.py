class DomainError(Exception):
  def __init__(self, message: str, entity_name: str = ""):
    self.entity_name = entity_name
    super().__init__(message)


class NotFoundError(DomainError):
  def __init__(self, entity_name: str, identifier: str):
    self.identifier = identifier
    super().__init__(
      message=f"Сущность '{entity_name}' с ID {identifier} не найдена.", entity_name=entity_name
    )


class AlreadyExistsError(DomainError):
  def __init__(self, entity_name: str, conflict_details: str):
    super().__init__(
      message=f"Сущность '{entity_name}' уже существует ({conflict_details}).",
      entity_name=entity_name,
    )


class BusinessRuleViolationError(DomainError):
  def __init__(self, entity_name: str, identifier: str, conflict_details: str):
    self.identifier = identifier
    super().__init__(
      message=f"Сущность '{entity_name}' с ID '{identifier}' нарушило бизнес-правило ({conflict_details})",
      entity_name=entity_name,
    )


class IsNoneError(DomainError):
  def __init__(self, entity_name: str, conflict_details: str):
    super().__init__(
      message=f"У сущности '{entity_name}' отсутствуют данные ({conflict_details})",
      entity_name=entity_name,
    )


class LoginFailedError(DomainError):
  def __init__(self, entity_name: str):
    super().__init__(message="Неверный логин или пароль", entity_name=entity_name)
