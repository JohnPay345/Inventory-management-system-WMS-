from dataclasses import asdict
from typing import Type, TypeVar

from sqlalchemy import inspect

T = TypeVar("T")


# Маппер ORM->Domain для плоских доменных сущностей без вложений
def map_orm_to_domain_flat(orm_object, domain_class: Type[T]) -> T:
  mapper = inspect(orm_object).mapper
  data = {attr.key: getattr(orm_object, attr.key) for attr in mapper.column_attrs}
  return domain_class(**data)


# Маппер Domain->ORM для плоских таблиц без вложений
def map_domain_to_orm_flat(domain_entity, orm_class: Type[T]) -> T:
  entity_data = asdict(domain_entity)
  return orm_class(**entity_data)
